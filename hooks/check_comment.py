#!/usr/bin/env python
"""
Checks code to see if there is adequate code comment, i.e. # comment line / # code line > REQUIRED_COMMENT_PERCENTAGE
"""
import atexit
import os
import yaml

from util import run_command

REQUIRED_COMMENT_PERCENTAGE = 15

class CheckComment(object):

    def should_process_file(self, filename):
        return True

    def __str__(self):
        return "<CheckComment>"

    def file_passes(self, temp_filename, original_filename=None):        
        atexit.register(os.remove, temp_filename)  # clean up after ourselves
        
        if original_filename is None:
            original_filename = temp_filename
           
        #import subprocess
        #p = subprocess.Popen(["/home/ha/Downloads/cloc-1.56.pl",  "--quiet",  "--yaml",  temp_filename], stdout=subprocess.PIPE)
        #out, err = p.communicate()
        
        out,  err,  returnCode = run_command('cloc --quiet --yaml ' + temp_filename)

        dataMap = yaml.load(out)
        scalaMap = dataMap['Scala']
        
        comment_percentage = scalaMap['comment'] * 100.0/ scalaMap['code']
        result_msg = "%s :: Code lines count: %s, Comment lines count: %s, Target comment percentage: %s, comment/code percentage: %s" % (str(self),  
                                                                                                                                          scalaMap['code'],  
                                                                                                                                          scalaMap['comment'], 
                                                                                                                                          REQUIRED_COMMENT_PERCENTAGE,  
                                                                                                                                          comment_percentage)
        
        if  comment_percentage < REQUIRED_COMMENT_PERCENTAGE:
            return False,  "FAIL " + result_msg            
        else:
            return True, "PASS " + result_msg

if __name__=="__main__":
    pass
