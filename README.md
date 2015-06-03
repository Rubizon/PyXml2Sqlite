PyXmlToSqlite
=============

Description:   Convert any XML file into a SQLite database.
               Enables you to use regular SQL stements to query the content of the XML file.

Author:        Ruben Roeffaers
Requirements:  python 2.x
               sqlite 3.x 

Usage:         python xml2sq3.py file1.xml [file2.xml, ... fileN.xml]

Outcome:       for every file: file1.xml2sq3.sq3

Example:

=== fruit.xml ===

   <fruit storage="fridge">
       <apple>
           <calories />
       </apple>
       <apple>
           <color>green</color>
       </apple>
   </fruit>

=== the magick ===
python xml2sq3.py fruit.xml


=== fruit.xml2sq3.sq3 ===

SELECT * FROM node;
   id  tag      level  value
   0   fruit    0
   1   apple    1
   2   calories 2
   3   apple    1
   4   color    2      'green'
   
SELECT * FROM relation;
   childNodeId  parentNodeId  levelDiff
   1            0             1
   2            1             1
   2            0             2
   3            1             1

SELECT * FROM attribute;
   nodeId      name           value
   0           storage        'fridge'

Just imagine what you can do now.
But remember,  with great tools comes great responsibility.
===
RuBiZoN
