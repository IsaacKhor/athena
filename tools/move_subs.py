#Connect to the project settings
import os, sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ["DJANGO_SETTINGS_MODULE"] = "ClarkCSHWGrader.settings"

from grader.models import *

if __name__ == "__main__":

    for sub in Submission.objects.all():
        try:
            old_filename = os.path.join(sub.get_directory_old(), sub.get_filename_old())
        except FileNotFoundError:
            print ("%s - OK\n" % os.path.join(sub.get_directory(), sub.get_filename()))
            continue
        
        new_filename = os.path.join(sub.get_directory(), sub.get_filename_old())
        os.renames(old_filename, new_filename)
        print("%s -> %s\n" % (old_filename, new_filename)
