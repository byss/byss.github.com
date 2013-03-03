#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  gen-unicode.py
#  byss.github.com
#
#  Created by Kirill byss Bystrov on 03.03.2013.
#  Copyright (c) 2013 Kirill byss Bystrov. All rights reserved.
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.
#

import sys
import time
import unicodedata
import htmlentitydefs

FOUT_TEMPLATE = 'unicode.{subst}.html'
MAXUNICODE = 0x110000
COLWIDTH = 0x20
INDEXCOLWIDTH = 0x10
PAGESIZE = 0x400
STYLES = '''\
{ts}table {{
{ts}	margin: 20px;
{ts}	counter-reset: line-number;
{ts}	border-collapse: collapse;
{ts}}}
{ts}table.index {{
{ts}	font-size: 75%;
{ts}}}
{ts}table.index, td, th {{
{ts}	border: 1px solid black;
{ts}}}
{ts}caption.index {{
{ts}	border: 0px;
{ts}	font-size: 125%;
{ts}	font-weight: bold;
{ts}	padding: 5px 10px;
{ts}}}
{ts}th.dead {{
{ts}	background-color: black;
{ts}}}
{ts}td.index {{
{ts}	border-style: dotted;
{ts}	padding: 5px;
{ts}}}
{ts}td.sym {{
{ts}	border-style: dotted;
{ts}	text-align: center;
{ts}	max-width: 2em;
{ts}}}
{ts}body {{
{ts}	text-align: center;
{ts}}}
{ts}div.centered {{
{ts}	display: inline-block;
{ts}}}
{ts}td.nav {{
{ts}	font-size: 125%;
{ts}	padding: 10px;
{ts}}}
{ts}.footnotes {{
{ts}	font-size: 75%;
{ts}	text-align: right;
{ts}}}
{ts}p.index-link {{
{ts}	font-variant: small-caps;
{ts}}}
'''

#################################################################################

def hexdig (num):
	return (hex (num) [2:]).upper ().rjust (4, '0')

def log (msg = '', level = 'D', *args, **kwargs):
	level_text = {
		'I': 'Info ',
		'W': 'Warn ',
		'E': 'Err  ',
		'F': 'Fatal',
	}.get (level, 'Debug')

	args_str = ', '.join ([str (a) for a in args])
	kwargs_str = ', '.join ([str (k) + ' = ' + str (kwargs [k]) for k in kwargs])
	addn_str = ' (' + ', '.join ([s for s in [args_str, kwargs_str] if len (s)]) + ')' if len (args_str) or len (kwargs_str) else ''
	time_str = '{clock:09.6f}'.format (clock = time.clock ())
	sys.stderr.write (time_str + ' [' + level_text + '] ' + msg + addn_str + '\n')

def fatal (msg, status = 1, *args, **kwargs):
	log (msg, 'F', *args, **kwargs)
	sys.exit (status)

def pagechars (page_n):
	return 'U+' + hexdig (page_n * PAGESIZE) + '&nbsp;&mdash; ' + 'U+' + hexdig ((page_n + 1) * PAGESIZE - 1)

def pagelink (page_n):
	return FOUT_TEMPLATE.format (subst = hexdig (page_n * PAGESIZE))

if MAXUNICODE % COLWIDTH:
	fatal ('Wrong columns count', MAXUNICODE = hex (MAXUNICODE), COLWIDTH = hex (COLWIDTH))
if PAGESIZE % COLWIDTH:
	fatal ('Wrong page size (for symbols page)', PAGESIZE = hex (PAGESIZE), COLWIDTH = hex (COLWIDTH))
if MAXUNICODE % PAGESIZE:
	fatal ('Wrong page size (for index page)', MAXUNICODE = hex (MAXUNICODE), PAGESIZE = hex (PAGEISIZE))
if (MAXUNICODE / PAGESIZE) % INDEXCOLWIDTH:
	fatal ('Wrong index columns count', MAXUNICODE = hex (MAXUNICODE), IDNDEX_LENGTH = hex (MAXUNICODE / PAGESIZE), INDEXCOLWIDTH = hex (INDEXCOLWIDTH))

index_fn = FOUT_TEMPLATE.format (subst = 'index')
fout = open (index_fn, 'wt')
if not fout:
	fatal ('Cannot open output file', 2, filename = index_fn)

log ('Writing index')

fout.write ('''\
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
	<head>
		<title>Unicode Characters Map Index</title>
		<meta http-equiv="content-type" content="text/html; charset=UTF-8" />
		<style type="text/css">
{css}
		</style>
	</head>
	<body>
		<div class="centered">
			<table class="index">
				<caption class="index">Unicode Characters Map Index</caption>
'''.format (css = STYLES.format (ts = '\t' * 3)))

for row in xrange (MAXUNICODE / PAGESIZE / INDEXCOLWIDTH):
	fout.write ('''\
				<tr>
''')
	for col in xrange (INDEXCOLWIDTH):
		page_n = row * INDEXCOLWIDTH + col
		fout.write ('''\
					<td class="index"><a href="{file}">{link_text}</a></td>
'''.format (file = pagelink (page_n),
            link_text = pagechars (page_n),
           ))

	fout.write ('''\
				</tr>
''')

fout.write ('''\
			</table>
		</div>
	</body>
</html>
''')

fout.close ()

hdr_digits_num = len (hex (COLWIDTH)) - 2

for page_n in xrange (MAXUNICODE / PAGESIZE):
	fn = pagelink (page_n)
	fout = open (fn, 'wt')
	if not fout:
		fatal ('Cannot open output file', 3, filename = fn)

	log ('Writing table', filename = fn, total = hexdig (MAXUNICODE))

	prev_fn = pagelink (page_n - 1) if page_n else None
	prev_link = '<a href="' + prev_fn + '">&larr;&nbsp;' + pagechars (page_n - 1) + '</a>' if prev_fn else '&larr;&nbsp;'
	next_fn = pagelink (page_n + 1) if page_n < MAXUNICODE / PAGESIZE else None
	next_link = '<a href="' + next_fn + '">' + pagechars (page_n + 1) + '&nbsp;&rarr;</a>' if next_fn else '&nbsp;&rarr;'

	fout.write ('''\
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
	<head>
		<title>Unicode Characters Map ({chars})</title>
		<meta http-equiv="content-type" content="text/html; charset=UTF-8" />
		<style type="text/css">
{css}
		</style>
	</head>
	<body>
		<div class="centered">
			<p class="index-link">
				<a href="{index_fn}">Go to Index</a>
			</p>
			<table>
				<tr>
					<td rowspan="{rowsnum}" class="nav">
						{prev_link}
					</td>
					<th class="dead" />
'''.format (chars = pagechars (page_n),
            css = STYLES.format (ts = '\t' * 3),
            prev_link = prev_link,
            rowsnum = PAGESIZE / COLWIDTH + 1,
            index_fn = index_fn,
           ))

	for hdr in xrange (COLWIDTH):
		fout.write ('''\
  				<th>+{hdr}</th>
'''.format (hdr = hexdig (hdr) [-hdr_digits_num:]))

	fout.write ('''\
					<td rowspan="{rowsnum}" class="nav">
						{next_link}
					</td>
				</tr>
'''.format (next_link = next_link, rowsnum = PAGESIZE / COLWIDTH + 1))

	for row in xrange (PAGESIZE / COLWIDTH):
		row_begin = page_n * PAGESIZE + row * COLWIDTH
		fout.write ('''\
				<tr>
					<th>{row}+</th>
'''.format (row = hexdig (row_begin)))
		for col in xrange (COLWIDTH):
			char_n = row_begin + col
			try:
				name_str = '; NAME: ' + unicodedata.name (unichr (char_n))
			except ValueError:
				name_str = ''
			html_str = '; HTML: &amp;' + htmlentitydefs.codepoint2name [char_n] + ';' if char_n in htmlentitydefs.codepoint2name else ''
			fout.write ('''\
					<td class="sym"><span title="HEX: {sym_hex}; DEC: {sym_dec}{name_str}{html_str}">&#x{sym};</span></td>
'''.format (sym = hexdig (char_n), sym_hex = hexdig (char_n), sym_dec = char_n, name_str = name_str, html_str = html_str))

		fout.write ('''\
				</tr>
''')

	fout.write ('''\
			</table>
			<p class="footnotes">
				<a href="http://validator.w3.org/check?uri=referer">
					<img src="http://www.w3.org/Icons/valid-xhtml11" alt="Valid XHTML 1.1" height="31" width="88" />
				</a>
				<a href="http://jigsaw.w3.org/css-validator/check/referer">
					<img style="border:0;width:88px;height:31px" src="http://jigsaw.w3.org/css-validator/images/vcss" alt="Valid CSS!" />
				</a>
			</p>
  	</div>
	</body>
</html>
''')

	fout.close ()
