#!/usr/bin/perl -w


#BEGIN {
#    open STDERR, ">&", \*STDOUT or print "$0: dup: $!";
#}
use strict;

#-----------------------------------#
#  1. Create a new Perl CGI object  #
#-----------------------------------#

use CGI;
my $query = new CGI;


#----------------------------------#
#  2. Print the doctype statement  #
#----------------------------------#

print $query->header;

#----------------------------------------------------#
#  3. Start the HTML doc, and give the page a title  #
#----------------------------------------------------#

print $query->start_html('Grouping program prototype');
my $filename;
my $content;
my $fh;

if (!$query->param) {

	$filename = "default.txt";
	$content = do {
		local $/ = undef;
		open ($fh, "<", $filename)
			or die "could not open $filename: $!";
		<$fh>;
	};
	print $query->start_form;
	print $query->textarea(-name=>'TEXT_AREA',
        	-default=>$content,
		-rows=>40,
		-columns=>120);
	print $query->br;
	print $query->submit(-value=>'Submit your grouping problem');
	print $query->end_form;

} else {

	print $query->h3('Here\'s what you entered:');

	my $yourText = $query->param('TEXT_AREA');

	$filename = 'test1.txt';
	open($fh, '>', $filename) or die "Could not open file '$filename' $!";
	print $fh $yourText;
	close $fh;
	system("/home/hnaves/public_html/cgi-bin/solve.py test1.txt > output.log");

	print "<pre>\n";
	print $yourText;
	print "</pre>\n";

	$filename = "output.log";
	$content = do {
		local $/ = undef;
		open ($fh, "<", $filename)
			or die "could not open $filename: $!";
		<$fh>;
	};

	print $query->h3('Solution:');
	print "<pre>\n";
	print $content;
	print "</pre>\n";
}

#-------------------------#
#  5. End the HTML page.  #
#-------------------------#

print $query->end_html;
