import os
import sys
import re
from shutil import copyfile, rmtree
from lxml import etree

def find_roots(rst_tree):
    nodes = rst_tree.xpath('/rst/body/*') #/not(@parent)')
    result = []
    for node in nodes:
        if node.get('parent') is None:
            result.append(node.get("id"))

    return result

def write_tree(tree, rootid, filename):
    segments = []
    queue = []
    groups = []
    root = etree.XML('<rst><header></header><body></body></rst>')
    header = root.xpath('/rst/header')[0]
    header.extend(tree.xpath('/rst/header/*'))
    body = root.xpath('/rst/body')[0]

    root_node = tree.xpath(f'/rst/body/group[@id={rootid}]')
    if len(root_node):
        groups.extend(root_node)
        queue.extend(root_node)
    else:
        segments.extend(tree.xpath(f'/rst/body/segment[@id={rootid}]'))
    
    while len(queue):
        group = queue.pop(0)
        id = group.get('id')
        queue.extend(tree.xpath(f'/rst/body/group[@parent={id}]'))
        groups.extend(tree.xpath(f'/rst/body/group[@parent={id}]'))
        segments.extend(tree.xpath(f'/rst/body/segment[@parent={id}]'))
    
    body.extend(segments)
    body.extend(groups)

    tree = etree.ElementTree(root)
    tree.write(filename, xml_declaration=False, encoding='utf-8')

if __name__ == "__main__":
    path = ''
    if len(sys.argv) >= 2:
        path = sys.argv[1]
        print('Read files from: {}'.format(path))
    else:
        print("\t The required <filepath> is missing. \n")
        print("Usage: python3 split_rs3.py <filepath> \n")
        exit()
    
    rst   = etree.parse(path)
    roots = find_roots(rst)

    if len(roots) < 2:
        print(f'File with less than 2 root nodes was no splitted: {path}')
        exit()

    for index, rootid in enumerate(roots):
        filename = f'{path}_{index}.rs3'
        write_tree(rst, rootid, filename)
        print(f'File created: {filename}')
