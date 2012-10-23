from distutils.core import setup

#This is a list of files to install, and where
#(relative to the 'root' dir, where setup.py is)
#You could be more specific.
files = ["res/*"]

setup(name = "axiometic",
    version = "0.2ubuntu3",
    description = "Axiometic: GUI companion for AXIOME",
    author = "Michael Hall",
    author_email = "hallm2533@gmail.com",
    url = "http://neufeld.github.com/",
    #Name the folder where your packages live:
    #(If you have other packages (dirs) or modules (py files) then
    #put them into the package directory - they will be found 
    #recursively.)
    packages = ['python_axiometic'],
    #'package' package must contain files (see list above)
    #I called the package 'package' thus cleverly confusing the whole issue...
    #This dict maps the package name =to=> directories
    #It says, package *needs* these files.
    package_data = {'python_axiometic' : files },
    #'runner' is in the root.
    scripts = ["axiometic"],
    long_description = """Axiometic is a GUI companion for AXIOME that guides the user through the creation of a .ax AXIOME configuration file.""" 
)
