
#
#   Copyright (C) 2007-2013 Alibaba Group Holding Limited
#
#   This program is free software;you can redistribute it and/or modify
#   it under the terms of the GUN General Public License version 2 as
#   published by the Free Software Foundation.
#
# dealinfo
#   check the info_file that record the coverage info,if there exists 
#   some relative path then replace it by absolute path

import sys
import os
import string
import shutil
import getopt
import subprocess
'''
whether the info file is valid?
'''
def check_file(infofile):
    if not os.path.exists(infofile):
        print ("%s does not exist")%infofile
	return False
    input = open(infofile,'r');
    valid_info = False
    alllines = input.readlines();
    for line in alllines:
	if line.startswith("end_of_record"):
		valid_info = True
    return valid_info
	
'''
Store line-numbers of the validcodes
'''
def store_line_numbers(filename):
    validlinenums = []
    if not os.path.exists(filename):
        print 'Error:file -%s does not exist.'%filename
        return []
        
    input = open(filename,'r')
    validlinenums = [0]*(len(input.readlines())+1)
    input.close;
    input = open(filename,'r');
        
    try:
        rFlag =0            # 1:the match not be finished  0: finished
        numbers = 0;
        line = input.readline()
        while line:
            numbers += 1;
            commentnum = string.find(line,'/*')
            if commentnum != -1 and line[:commentnum].strip()!="/":  #find a /*
                if commentnum > 1 and line[:commentnum].strip()!="": #before the '/*' has valid code, such as: 'int func()  /* it is a function....'
                    validlinenums[numbers]= numbers
                rFlag = 1
                commentnum = string.find(line,'*/')
                if commentnum != -1:  # the end comment '*/' in the same line 
                    rFlag = 0
                else:  # the end comment '*/' not in the same line
                    multirowcomments = 1
                    line = input.readline()
                    while line:
                        numbers += 1;
                        commentnum = string.find(line,'*/')
                        if commentnum != -1:
                            rFlag = 0
                            break
                        line = input.readline()
                    if not line:
                        print 'Match /*..............*/ error'
            else:  # deal with //
                commentnum = string.find(line,'//')
                if commentnum == -1:
                    if line.strip()!="":  #not an empty line
                        validlinenums[numbers]=numbers
                elif commentnum != -1 and (not rFlag):
                    if commentnum > 1 and line[:commentnum].strip()!="":
                        validlinenums[numbers]=numbers
            line = input.readline()
    except:
        print 'Error:unexcept error.'+filename
        input.close

    return validlinenums;
    
'''
(1)Open the info-file that generated by lcov;
(2)Search the opened info-file for path of the source file 
(3)Store the paths in an array whose name is files

'''
def read_from_info(infofile,files):
    if not os.path.exists(infofile):
        print ("%s does not exist")%infofile
    input = open(infofile,'r');
    alllines = input.readlines();
    for line in alllines:
        if line.startswith("SF:"):
            files.append(line[3:len(line)-1]);
 
'''
(1)Open the info_file for read
(2)Insert the valid-codes's number that not been included in the info_file by calling the insert_into_info()
(3)Append the coverage infomations of those files that didn't excute  by calling the append_to_info
'''   
def write_to_info(infofile,filename,rows):
    input = open(infofile,'r');
    line = input.readline();
    findfile = False;
    insertlocation = 0;
    while line and not findfile:
        insertlocation +=1
        if line[3:len(line)-1] == filename:
            line = input.readline()
            while line:
                if line.startswith("end_of_record"):
                    findfile = True;
                    break;
                line = input.readline();
        line = input.readline()
        
    if not findfile:
        append_to_info(rows,filename,infofile);

                
def append_to_info(array,filename,infofile):
    input = open(infofile,'r');
    copy_file = infofile+".bak"
    output = open(copy_file,"a");
    line = input.readline();
    while line:
        output.write(str(line));
        line = input.readline();
    input.close;

    output.write("TN:\n");
    output.write("SF:"+filename+"\n");

    for row in array:
        if array[row] != 0:
            output.write("DA:"+str(row)+",0"+"\n");
    output.write("end_of_record\n");
    output.close;

    rename = "mv "+copy_file+" " +infofile;
    subprocess.call(rename,shell=True)


def file_in_info(filename,files):
    for file in files:
        if filename == file:
            return True;
    return False;

def count_files(path, files):
    for root, dirs, mfiles in os.walk(path):
        for filespath in mfiles:
            dirname = os.path.join(root, filespath)
            if dirname.endswith(".gcno"):
                preFile = dirname.split(".gcno")[0];
                ccFile = preFile+".cc"
                cppFile = preFile+".cpp"
                cFile = preFile+".c"
              
                if os.path.exists(ccFile) and not file_in_info(ccFile,files):
                    files.append(ccFile);
                elif os.path.exists(cppFile) and not file_in_info(cppFile,files):
                    files.append(cppFile);
                elif os.path.exists(cFile) and not file_in_info(cFile,files):
                    files.append(cFile);
   
'''
by calling this function to modify the info-file           
'''
def modify_info(infofile,basepath):
    files = [];
    if not os.path.exists(infofile):
        print ("%s does not exits,the tool will exit")%infofile
        exit(1)
    read_from_info(infofile,files);
    count_files(basepath,files);
    for file in files:
       rows = store_line_numbers(file)
       write_to_info(infofile,file,rows);
      

