# playwav.pl
# CGI Perl script that uses playwav.exe to play a wave file on a web server.
# Copyright (c) 2001 by Mu-Consulting (www.muconsulting.com)
# This Perl script may be modified freely for your own needs.

# The following two variables must changed to reflect your file paths.

# This is the directory where wav files are located in.
# Make sure to keep the trailing "\\" characters.
$mediafileprefix = "c:\\inetpub\\wwwroot\\media\\";

# This is the full path the the playwav.exe file.
$playwaveexepath = "c:\\inetpub\\wwwroot\\bin\\playwav.exe";

# Parse HTTP parameters
$querystring = $ENV{'QUERY_STRING'};
@pairs = split(/&/, $querystring);
foreach $pair (@pairs)
	{
	($name, $value) = split(/=/, $pair);
	$value =~ tr/+/ /;
	$value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
	$FORM{$name} = $value;
	}

if (($#argv < 0) & $querystring eq "")
	{
	&PrintForm;
	}

$mediafile = $FORM{'f'};

print "Content-type: text/html\n";
print "Cache-Control: no-cache\n\n";
print "<html>\n<head>\n";
print "<title>Play Wav File</title>\n";
print "</head>\n";
print "<body>\n";

if ($mediafile =~ /[^a-zA-z0-9-]/)
	{
	print "You entered an invalid media file name.\n";
	print "</body>\n";
	print "</html>\n";
	exit;
	}

print "<font size=+2>\n";
print "Playing media file \"$mediafile\"...<br>\n";
print "</font>\n";

$mediafilepath = "$mediafileprefix$mediafile.wav";

print "<pre>\n";

# Run playwave.exe and output results
print `$playwaveexepath \"$mediafilepath\"`;

print "</pre>\n";
print "<br><hr>\n";
print "</body>\n";
print "</html>\n";

sub PrintForm
	{
	print "Content-type: text/html\n\n";
	print "<html>\n<head>\n";
	print "<title>Play Wav File</title>\n";
	print "</head>\n";
	print "<body>\n";
	print "You entered an invalid command.\n";
	print "</body>\n";
	print "</html>\n";
	exit;
	}
