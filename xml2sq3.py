#!/usr/bin/python


#
# description   convert a xml to a sq3 file
# author        ruben roeffaers
# requirements  sqlite3 installed
# usage         python xml2sq3.py xmlfile1 [ ,xmlfile2 [ ,xmlfile3 [,...] ] ]
# outcome       *.xml2sq3.sq3 sqlite3 database file
#
# database description
#
#   The XML:
#   
#   <fruit storage="fridge">
#       <apple>
#           <calories />
#       </apple>
#       <apple>
#           <color>green</color>
#       </apple>
#   </fruit>
#
#   Becomes the sqlite3 file:
#
#   node (-tale)
#   id  tag      level  value
#   0   fruit    0
#   1   apple    1
#   2   calories 2
#   3   apple    1
#   4   color    2      'green'
#   
#   relation (-table)
#   childNodeId  parentNodeId  levelDiff
#   1            0             1
#   2            1             1
#   2            0             2
#   3            1             1
#
#   attribute (-table)
#   nodeId      name           value
#   0           storage        'fridge'
# 

import sys
import xml.etree.ElementTree as ET
import os
import cStringIO
import copy



# dynamic storage info for nodes
class Data(object):
    pass




def emitNode( output, separator, ni ):

    print >> output, separator.join( ( \
        str(ni.idx), \
        ni.tag,   \
        str(ni.level), \
        "NULL" if ni.value==None else ni.value ) )




def emitAttributes( output, separator, ni ):

    for k, v in ni.attributes.items():
        print >> output, separator.join( ( str(ni.idx), k, v ) )




def emitRelations( output, separator, ni, parentIdx, info ):

    if parentIdx != None:
        pi = info[parentIdx]
        print >> output, separator.join( ( \
            str(ni.idx), str(pi.idx), str(ni.level-pi.level) ) )
            
        emitRelations( output, separator, ni, pi.parentNodeIdx, info )




def emit( xmlfile, info ):
    
    # assumption: following seperator literal isn't present anywhere in the 
    #             entire xml content.
    separator = "| @#$& |"
    
    nodefile       = xmlfile + ".xml2sq3.node.csv"
    attributefile  = xmlfile + ".xml2sq3.attribute.csv"
    relationfile   = xmlfile + ".xml2sq3.relation.csv"
    
    nodeoutput       = open( nodefile,      'w' )
    attributeoutput  = open( attributefile, 'w' )
    relationoutput   = open( relationfile,  'w' )
    
    for idx in range(0, len(info)):
        ni = info[idx]

        emitNode(       nodeoutput,      separator, ni )
        emitAttributes( attributeoutput, separator, ni )
        emitRelations(  relationoutput,  separator, ni, ni.parentNodeIdx, info )
        
        print "xml2sq3: emitting: " + (str(idx+1)) + "/" + str(len(info)) + (4 * ni.level * " ") +  " <" + ni.tag + ">"
    
    nodeoutput.close()
    attributeoutput.close()
    relationoutput.close()
    
    outputfile = xmlfile + ".xml2sq3.sql"
    output = open( outputfile, 'w' )
    
    print >> output, "PRAGMA synchronous  = OFF;"       #
    print >> output, "PRAGMA locking_mode = EXCLUSIVE;" #
    print >> output, "PRAGMA page_size    = 16384;"     # Default is 1024
    print >> output, "PRAGMA cache_size   = 40000;"     # Default is 2000; Cache will be 625MB
    print >> output, "PRAGMA temp_store   = FILE;"

    print >> output, "CREATE TABLE node( id INTEGER PRIMARY KEY, tag TEXT, level TEXT, value TEXT );"
    print >> output, "CREATE TABLE relation( childNodeId INTEGER, parentNodeId INTEGER, levelDiff INTEGER, PRIMARY KEY( childNodeId, parentNodeId ) );"
    print >> output, "CREATE TABLE attribute( nodeId, name, value, PRIMARY KEY( nodeId, name ) );";

    print >> output, ".separator \"" + separator.strip() + "\""
    print >> output, ".import " + nodefile      + " node"
    print >> output, ".import " + attributefile + " attribute"
    print >> output, ".import " + relationfile  + " relation"
    
    
    print >> output, "CREATE INDEX idx_node_id_level  ON node( id,  level );"
    print >> output, "CREATE INDEX idx_node_tag_value ON node( tag, value );"

    print >> output, "CREATE INDEX idx_attribute_name_value ON attribute( name, value );"
    
    print >> output, "CREATE INDEX idx_relation_childnodeid_leveldiff  ON relation( childnodeid,  leveldiff );"
    print >> output, "CREATE INDEX idx_relation_parentnodeid_leveldiff ON relation( parentnodeid, leveldiff );"
    # print >> output, "INSERT 'Provoke exit trough bail option. all things went just fine. this is not a';"
    
    output.close()

    dbfile = xmlfile + ".xml2sq3.sq3"
    if os.path.isfile( dbfile ):
        os.remove( dbfile )
    
    print "xml2sq3: filling '" + dbfile + "' ..."
    os.system( "sqlite3 " + dbfile + " -cmd '.read " + outputfile + "' .quit"  )

    os.remove( nodefile )
    os.remove( attributefile )
    os.remove( relationfile )
    os.remove( outputfile )



def collectInfo( node, level=0, parentNodeIdx=None, info=[] ):

    ni               = Data()
    ni.tag           = node.tag
    ni.level         = level
    ni.attributes    = {}
    ni.parentNodeIdx = parentNodeIdx
    ni.value         = None
    
    # iterate attributes
    for k, v in node.items():
        ni.attributes[k]=v.encode('utf-8')


    # handle value if no childs
    if len(node) < 1:
        ni.value = "" if node.text==None else node.text.encode('utf-8')
    
    
    # predict index and add nodeInfo
    ni.idx = len(info)
    info.append(ni)
    
    
    # recursive call for child nodes
    for childNode in node:
        collectInfo( childNode, level+1, ni.idx, info )
        
        
    #print "collectInfo: " + (" " * 4 * level) + node.tag + " #" + str(ni.idx)
    
    
    return info
    
    
    
    
def main():

    if len(sys.argv)<2:
        sys.exit(os.EX_NOINPUT)

    for i in range(1,len(sys.argv)):
        
        xmlfile = sys.argv[i]


        print "xml2sq3: parsing '" + xmlfile + "' ..."
        try:
            tree = ET.parse(xmlfile)
        except ET.ParseError:
            continue
        
        
        print "xml2sq3: collecting info ..."
        emit( xmlfile, collectInfo( tree.getroot() ) )




if __name__ == '__main__':
    main()



