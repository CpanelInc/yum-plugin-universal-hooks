#!/usr/bin/perl

# Copyright (c) 2021, cPanel, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

use strict;
use warnings;

# We only support the DPkg:: version of these hook points, if that ever changes
#  this will need updated here and in apt-universal-hooks.conf
my %hook_points = (
    "Pre-Invoke"       => 1,
    "Pre-Install-Pkgs" => 1,
    "Post-Invoke"      => 1,
);

my $hook_point = $ARGV[0];
die "Invalid hook point name “$hook_point”\n" if !exists $hook_points{$hook_point};

my $basedir = "/etc/apt/universal-hooks";

my $txn_id = _get_txn_id();
my $txpath = "/tmp/apt.$txn_id.txn-pkgs";

_debug_out("DEBUG:\n\tHook Point: $hook_point\n\t/tmp/apt.$txn_id.txn-pkgs") if $ENV{APT_UNIVERSAL_HOOKS_DEBUG};

if ( exists $ENV{APT_HOOK_INFO_FD} ) {
    open( my $apt_fh, "<&=", $ENV{APT_HOOK_INFO_FD} ) or die "open <&= $ENV{APT_HOOK_INFO_FD} failed: $!\n";
    _debug_out("have APT_HOOK_INFO_FD") if $ENV{APT_UNIVERSAL_HOOKS_DEBUG};

    my %pkgs;
    while ( my $line = <$apt_fh> ) {
        chomp $line;
        _debug_out("APT_HOOK_INFO_FD LINE: $line") if $ENV{APT_UNIVERSAL_HOOKS_DEBUG};

        if ( $line =~ m/^(\S+) .* \*\*(?:REMOVE|CONFIGURE)\*\*$/ ) {
            my $pkg_from_version_2_line = $1;
            _debug_out("APT_HOOK_INFO_FD PKG FOUND: $pkg_from_version_2_line") if $ENV{APT_UNIVERSAL_HOOKS_DEBUG};

            $pkgs{$pkg_from_version_2_line}++;
        }
    }

    close $apt_fh;

    open( my $txn_fh, ">", $txpath ) or die "Could not open for write “$txpath”: $!\n";
    for my $pkg ( sort keys %pkgs ) { print {$txn_fh} "$pkg\n"; }
    close $txn_fh;
}

if ( -e $txpath ) {

    my @pkgs;
    open( my $txn_fh, "<", $txpath ) or die "Could not open for read “$txpath”: $!\n";
    while ( my $pkg = <$txn_fh> ) {
        chomp $pkg;
        push @pkgs, $pkg;
    }
    close $txn_fh;

    _run_pkg_dirs( $basedir => $hook_point, $txpath => \@pkgs );
    _run_dir("$basedir/$hook_point");
}
else {
    warn "Packages involved is unknown; only doing packageless universal hooks in $basedir/$hook_point (if any)\n" if $hook_point ne 'Pre-Invoke';

    _run_dir("$basedir/$hook_point");
}

if ( $hook_point eq "Post-Invoke" ) {
    if ( $ENV{APT_UNIVERSAL_HOOKS_DEBUG} ) {
        _debug_out("Not removing “$txpath”");
    }
    else {
        unlink $txpath;
    }
}

exit(0);

###############
#### helpers ##
###############

sub _get_txn_id {
    my $res;
    chomp( my $pp = `cut -f4 -d ' ' /proc/$$/stat` );
    chomp( my $gp = `cut -f4 -d ' ' /proc/$pp/stat` );
    chomp( my $gg = `cut -f4 -d ' ' /proc/$gp/stat` );

    if ( $hook_point eq "Pre-Install-Pkgs" ) {
        chomp( $res = `ps -o ppid= -o lstart= -o cmd= -p $gp` );
    }
    else {
        chomp( $res = `ps -o ppid= -o lstart= -o cmd= -p $gg` );
    }

    $res =~ s/\s+/ /g;
    $res =~ s{/}{__SLASH__}g;

    if ( $ENV{APT_UNIVERSAL_HOOKS_DEBUG} ) {
        _debug_out("TXN PIDs: $$, $pp, $gp, $gg");
        _debug_out("TXN Uniq: -$res-");
    }

    return $res;
}

sub _debug_out {
    my ($str) = @_;
    print "DEBUG ($hook_point) — $str\n";
    return;
}

sub _run_dir {
    my ( $dir, $args ) = @_;

    $dir =~ s/\*$//;
    $dir =~ s{/+$}{};

    return if !-d $dir;

    for my $script ( sort glob("$dir/*") ) {
        _debug_out("Script: $script") if $ENV{APT_UNIVERSAL_HOOKS_DEBUG};

        if ( -x $script ) {
            $script .= " $args"              if length $args;
            _debug_out("Executing: $script") if $ENV{APT_UNIVERSAL_HOOKS_DEBUG};

            system($script) && warn "!!!! “$script” did not exit cleanly: $?\n";
        }
        else {
            print "!!!! $script is not executable\n";
        }
    }

    return 1;
}

sub _run_pkg_dirs {
    my ( $basedir, $hookpoint, $pkgsfile, $pkgs_ar ) = @_;

    my $wc_dir        = "$basedir/multi_pkgs/$hookpoint";
    my $wildcard_list = {};
    for my $path ( glob("$wc_dir/*") ) {
        if ( -d $path ) {
            my $name = $path;
            $name =~ s{.*/([^/]+)$}{$1};

            my $regx = $name;
            $regx =~ s/__WILDCARD__/\.*/g;
            $wildcard_list->{$name} = qr/^$regx$/;
        }
    }

    my $wildcard_to_run = {};

    for my $pkg ( @{$pkgs_ar} ) {
        _run_dir("$basedir/pkgs/$pkg/$hookpoint");

        for my $wc ( keys %{$wildcard_list} ) {
            if ( $pkg =~ $wildcard_list->{$wc} ) {
                $wildcard_to_run->{$wc} = 1;
            }
        }
    }

    for my $wc_run ( keys %{$wildcard_to_run} ) {
        _run_dir( "$wc_dir/$wc_run", "--pkg_list=" . quotemeta($pkgsfile) );
    }

    return 1;
}
