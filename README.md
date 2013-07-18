PyXmlToSqlite
=============

description   convert a xml to a sq3 file
author        ruben roeffaers
requirements  sqlite3 installed
usage         python PyXml2Sqlite xmlfile1 [ ,xmlfile2 [ ,xmlfile3 [,...] ] ]
outcome       *.xml2sq3.sq3 sqlite3 database file

database description

The XML:

<fruit storage="fridge">
  <apple>
    <calories />
  </apple>
  <apple>
    <color>green</color>
  </apple>
</fruit>

Becomes the sqlite3 file:

node (-tale)
id  tag      level  value
0   fruit    0
1   apple    1
2   calories 2
3   apple    1
4   color    2      'green'
 
relation (-table)
childNodeId  parentNodeId  levelDiff
1            0             1
2            1             1
2            0             2
3            1             1

attribute (-table)
nodeId      name           value
0           storage        'fridge'

