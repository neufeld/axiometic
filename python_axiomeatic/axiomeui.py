#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  axiomeui.py
#  
#  Copyright 2012 Michael Hall <hallm2533@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#       
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

#TODO: Catch errors when removing and no selection

import pygtk, os, sys
pygtk.require("2.0")
import gtk, gobject, gio
#from gi.repository import Gtk, gobject, Gio

def determine_path():
    """Borrowed from wxglade.py"""
    try:
        root = __file__
        if os.path.islink(root):
            root = os.path.realpath(root)
        return os.path.dirname (os.path.abspath(root))
    except:
        print "I'm sorry, but something is wrong."
        print "There is no __file__ variable. Please contact the author."
        sys.exit()

class Analysis:
	def __init__(self):
		#Widget info consists of a four-tuple, with 
		#( widget, type (str), required (bool), xml parameter name (str) ) 
		self.widgetInfo = list()
		self.widgetContainer = None
		self.once = False
		self.XMLName = None
		
	def is_only_once(self):
		return self.once
		
	def required_fields_empty(self):
		#Go through each widget, and, if required, check widget is
		#not empty, using appropriate check for the type
		for widget in self.widgetInfo:
			if ( widget[2] ):
				if ( widget[1] == "Entry" ):
					if ( widget[0].get_text() == "" ):
						return True
				elif ( widget[1] == "ComboBoxText" ):
					if  ( widget[0].get_active_text() == "" ) | ( widget[0].get_active_text() == None ):
						return True
		return False
		
	def get_xml_name(self):
		return self.XMLName
		
	def get_parameter_string(self):
		parameters = ""
		for widget in self.widgetInfo:
			if ( widget[1] == "Entry" ):
				if ( ( widget[0].get_text() != "" ) & ( widget[0].get_text() != None ) ):
					parameters += " " +  widget[3] + "=\"" + widget[0].get_text() + "\""
			elif ( widget[1] == "ComboBoxText" ):
				if ( ( widget[0].get_active_text() != "" ) & ( widget[0].get_active_text() != None ) ):
					parameters += " " +  widget[3] + "=\"" + widget[0].get_active_text() + "\""
		return parameters
		
class AlphaDiv(Analysis):
	def __init__(self):
		Analysis.__init__(self)
		self.once = True
		self.XMLName = "alpha"
		
		
	def construct_widgets(self):
		#No widgets required
		label = "Perform an Alpha Diversity analysis (ie, QIIME's Chao1 curves).\n \
		Will make use of multiple cores if the option is enabled."
		return self.widgetContainer, label
		
class BetaDiv(Analysis):
	def __init__(self):
		Analysis.__init__(self)
		self.XMLName = "beta"
		
		
	def construct_widgets(self):
		self.widgetContainer = gtk.Table(4, 2)
		label = "Do a QIIME beta diversity analysis and produce biplots and bubble plots.\n\n\
QIIME normally uses summarised taxa for the  plots, so the taxonomic level can \
be specified; if it is omitted, OTUs are used instead."
		lblLevel = gtk.Label("Level:")
		lblSize = gtk.Label("Size:")
		lblSize.set_tooltip_text("Rarefies library to specific size. 'auto' for smallest sample size. Default: none")
		lblTaxa = gtk.Label("Taxa:")
		lblTaxa.set_tooltip_text("Limits the number of taxa in biplot. Default: 10")
		lblBackground = gtk.Label("Background Colour:")
		lblBackground.set_tooltip_text("Plot background colour. Default: white")
		levelList = [ "All", "Life", "Domain", "Phylum", "Class", "Order", "Family", "Genus", \
		"Species", "Strain" ]
		cmbLevel = gtk.combo_box_new_text()
		for level in levelList:
			cmbLevel.append_text(level)
		txtSize = gtk.Entry()
		txtTaxa = gtk.Entry()
		txtBackground = gtk.Entry()
		self.widgetInfo.append((cmbLevel, "ComboBoxText", False, "level"))
		self.widgetInfo.append((txtSize, "Entry", False, "size"))
		self.widgetInfo.append((txtTaxa, "Entry", False, "taxa"))
		self.widgetInfo.append((txtBackground, "Entry", False, "background"))
		self.widgetContainer.attach(lblLevel, 0, 1, 0, 1, xpadding=5, ypadding=5)
		self.widgetContainer.attach(cmbLevel, 1, 2, 0, 1, yoptions=gtk.SHRINK, xpadding=5, ypadding=5)
		self.widgetContainer.attach(lblSize, 2, 3, 0, 1, xpadding=5, ypadding=5)
		self.widgetContainer.attach(txtSize, 3, 4, 0, 1, xpadding=5, ypadding=5)
		self.widgetContainer.attach(lblTaxa, 0, 1, 1, 2, xpadding=5, ypadding=5)
		self.widgetContainer.attach(txtTaxa, 1, 2, 1, 2, xpadding=5, ypadding=5)
		self.widgetContainer.attach(lblBackground, 2, 3, 1, 2, xpadding=5, ypadding=5)
		self.widgetContainer.attach(txtBackground, 3, 4, 1, 2, xpadding=5, ypadding=5)
		return self.widgetContainer, label
		
class BLAST(Analysis):
	def __init__(self):
		Analysis.__init__(self)
		self.once = True
		self.XMLName = "blast"
		
		
	def construct_widgets(self):
		self.widgetContainer = gtk.Table(4, 1)
		label = "Create a BLAST DB with the specified title, and using the \
specified blastdb creation command."
		lblTitle = gtk.Label("Title:")
		lblDBCmd = gtk.Label("BLAST DB Command:")
		txtTitle = gtk.Entry()
		cmbDBCmd = gtk.combo_box_new_text()
		cmbDBCmd.append_text("formatdb")
		cmbDBCmd.append_text("makeblastdb")
		self.widgetInfo.append((txtTitle, "Entry", False, "title"))
		self.widgetInfo.append((cmbDBCmd, "ComboBoxText", False, "command"))
		self.widgetContainer.attach(lblTitle, 0, 1, 0, 1, xpadding=5, ypadding=5)
		self.widgetContainer.attach(txtTitle, 1, 2, 0, 1, xpadding=5, ypadding=5)
		self.widgetContainer.attach(lblDBCmd, 2, 3, 0, 1, xpadding=5, ypadding=5)
		self.widgetContainer.attach(cmbDBCmd, 3, 4, 0, 1, yoptions=gtk.SHRINK, xpadding=5, ypadding=5)
		return self.widgetContainer, label

class CompareLibs(Analysis):
	def __init__(self):
		Analysis.__init__(self)
		self.once = True
		self.XMLName = "compare"
		
		
	def construct_widgets(self):
		self.widgetContainer = gtk.Table(2,1)
		label = "Compare libraries at the specified taxonomic level."
		lblLevel = gtk.Label("<span color=\"#FF0000\">Level:</span>")
		lblLevel.set_use_markup(True)
		levelList = [ "Life", "Domain", "Phylum", "Class", "Order", "Family", "Genus", \
		"Species", "Strain" ]
		cmbLevel = gtk.combo_box_new_text()
		for level in levelList:
			cmbLevel.append_text(level)
		self.widgetInfo.append((cmbLevel, "ComboBoxText", True, "level"))
		self.widgetContainer.attach(lblLevel, 0, 1, 0, 1, xpadding=5, ypadding=5)
		self.widgetContainer.attach(cmbLevel, 1, 2, 0, 1, yoptions=gtk.SHRINK, xpadding=5, ypadding=5)
		return self.widgetContainer, label

class Duleg(Analysis):
	def __init__(self):
		Analysis.__init__(self)
		self.XMLName = "duleg"
		
		
	def construct_widgets(self):
		self.widgetContainer = gtk.Table(2,1)
		label = "Compute a Dufrene-Legendre indicator species analysis on numerical \
metadata fields. Uses the specified p-value as the cut-off to be included in \
the indicator species list."
		lblPVal = gtk.Label("p Value:")
		txtPVal = gtk.Entry()
		self.widgetInfo.append((txtPVal, "Entry", False, "p"))
		self.widgetContainer.attach(lblPVal, 0, 1, 0, 1, xpadding=5, ypadding=5)
		self.widgetContainer.attach(txtPVal, 1, 2, 0, 1, xpadding=5, ypadding=5)
		return self.widgetContainer, label

class Heatmap(Analysis):
	def __init__(self):
		Analysis.__init__(self)
		self.once = True
		self.XMLName = "heatmap"
		
		
	def construct_widgets(self):
		#No widgets required
		label = "Create an OTU heatmap plot using QIIME."
		return self.widgetContainer, label

class Jackknife(Analysis):
	def __init__(self):
		Analysis.__init__(self)
		self.XMLName = "jackknife"
		
		
	def construct_widgets(self):
		self.widgetContainer = gtk.Table(2,1)
		label = "Create 2D and 3D PCoA plots based on jackknifing (repeated subsampling) \
of the OTU table using  QIIME's  jackknifed_beta_diversity.py script. Size \
parameter is optional must be a positive number no larger than the largest \
number of sequences in a sample."
		lblSize = gtk.Label("Size:")
		txtSize = gtk.Entry()
		self.widgetInfo.append((txtSize, "Entry", False, "size"))
		self.widgetContainer.attach(lblSize, 0, 1, 0, 1, xpadding=5, ypadding=5)
		self.widgetContainer.attach(txtSize, 1, 2, 0, 1, xpadding=5, ypadding=5)
		return self.widgetContainer, label

class MRPP(Analysis):
	def __init__(self):
		Analysis.__init__(self)
		self.XMLName = "mrpp"
		
		
	def construct_widgets(self):
		self.widgetContainer = gtk.Table(2,1)
		label = "Compute  Multi  Response  Permutation Procedure of within-versus \
among-group dissimilarities in R using the specified distance method."
		distancemethods = [ "manhattan", "euclidean", "canberra", "bray", "kulczynski", "jaccard", "gower", "altGower", "morisita", "horn", "mountford",  "raup", \
		"binomial", "chao", "cao" ]
		lblDistance = gtk.Label("Distance Method:")
		cmbDistance = gtk.combo_box_new_text()
		for method in distancemethods:
			cmbDistance.append_text(method)
		self.widgetInfo.append((cmbDistance, "ComboBoxText", False, "method"))
		self.widgetContainer.attach(lblDistance, 0, 1, 0, 1, xpadding=5, ypadding=5)
		self.widgetContainer.attach(cmbDistance, 1, 2, 0, 1, yoptions=gtk.SHRINK, xpadding=5, ypadding=5)
		return self.widgetContainer, label

class NMF(Analysis):
	def __init__(self):
		Analysis.__init__(self)
		self.XMLName = "nmf"
		
		
	def construct_widgets(self):
		self.widgetContainer = gtk.Table(2,1)
		label = "Compute Non-negative Matrix Factorization of the data using bases \
equal to the specified degree parameter. An appropriate degree parameter \
can be obtained by analysing an NMF Concordance plot for local maxima. \
Degree must be greater than 2, but less than 20."
		lblDegree = gtk.Label("<span color=\"#FF0000\">Degree:</span>")
		lblDegree.set_use_markup(True)
		txtDegree = gtk.Entry()
		self.widgetInfo.append((txtDegree, "Entry", True, "degree"))
		self.widgetContainer.attach(lblDegree, 0, 1, 0, 1, xpadding=5, ypadding=5)
		self.widgetContainer.attach(txtDegree, 1, 2, 0, 1, xpadding=5, ypadding=5)
		return self.widgetContainer, label
		
class NMFConcordance(Analysis):
	def __init__(self):
		Analysis.__init__(self)
		self.once = True
		self.XMLName = "nmf-concordance"
		
		
	def construct_widgets(self):
		#No widgets required
		label = "Compute a concordance plot of the data for use in determining an \
appropriate degree value to create an NMF plot. The local maxima of the \
concordance plot are appropriate to be used as the degree parameter of an \
NMF analysis."
		return self.widgetContainer, label
		
class NMFAuto(Analysis):
	def __init__(self):
		Analysis.__init__(self)
		self.once = True
		self.XMLName = "nmf-auto"
		
		
	def construct_widgets(self):
		#No widgets required
		label = "Compute a concordance plot, and automatically search it for local maxima, \
and then run an NMF analysis on each one. Note that this will run an NMF analysis \
on all local maxima, which is potentially computationally expensive and time consuming."
		return self.widgetContainer, label

class PCoA(Analysis):
	def __init__(self):
		Analysis.__init__(self)
		self.XMLName = "pcoa"
		
		
	def construct_widgets(self):
		self.widgetContainer = gtk.Table(2,1)
		label = "Create a 2D principal coordinate analysis plot using the two most \
significant dimensions. Plots an MDS plot, and if there is more than 1 numerical \
metadata field, a biplot will be created. Uses the specified distance method, \
and colours described in the \"Colour\" field of the metadata."
		distancemethods = [ "manhattan", "euclidean", "canberra", "bray", "kulczynski", "jaccard", "gower", "altGower", "morisita", "horn", "mountford",  "raup", \
		"binomial", "chao", "cao" ]
		lblDistance = gtk.Label("Distance Method:")
		cmbDistance = gtk.combo_box_new_text()
		for method in distancemethods:
			cmbDistance.append_text(method)
		self.widgetInfo.append((cmbDistance, "ComboBoxText", False, "method"))
		self.widgetContainer.attach(lblDistance, 0, 1, 0, 1, xpadding=5, ypadding=5)
		self.widgetContainer.attach(cmbDistance, 1, 2, 0, 1, yoptions=gtk.SHRINK, xpadding=5, ypadding=5)
		return self.widgetContainer, label

class RankAbundance(Analysis):
	def __init__(self):
		Analysis.__init__(self)
		self.once = True
		self.XMLName = "rankabundance"
		
		
	def construct_widgets(self):
		#No widgets required
		label = "Create a rank-abundance plot using QIIME."
		return self.widgetContainer, label

class RDP(Analysis):
	def __init__(self):
		Analysis.__init__(self)
		self.once = True
		self.XMLName = "rdp"
		
		
	def construct_widgets(self):
		self.widgetContainer = gtk.Table(4,2)
		label = "Change the parameters used for RDP classification. \
Confidence value is a numeric value between 0 and 1, where the \
default is 0.8 (for short reads, 0.5 is recommended). The \
taxonomy file and sequence file are specified only if you wish \
to use your own database for classification, otherwise it \
defaults to your configured QIIME default. The max memory (MB) value \
should be set to a higher value if using a custom database to prevent \
RDP from running out of memory (default is 1000)."
		lblConfidence = gtk.Label("Confidence:")
		lblTaxonomyFile = gtk.Label("Taxonomy File:")
		lblSeqFile = gtk.Label("Sequence File:")
		lblMaxMemory = gtk.Label("Max Memory (MB):")
		txtConfidence = gtk.Entry()
		txtTaxonomyFile = gtk.Entry()
		txtSeqFile = gtk.Entry()
		txtMaxMemory = gtk.Entry()
		self.widgetInfo.append((txtConfidence, "Entry", False, "confidence"))
		self.widgetInfo.append((txtMaxMemory, "Entry", False, "maxmemory"))
		self.widgetInfo.append((txtTaxonomyFile, "Entry", False, "taxfile"))
		self.widgetInfo.append((txtSeqFile, "Entry", False, "seqfile"))
		self.widgetContainer.attach(lblConfidence, 0, 1, 0, 1, xpadding=5, ypadding=5)
		self.widgetContainer.attach(txtConfidence, 1, 2, 0, 1, xpadding=5, ypadding=5)
		self.widgetContainer.attach(lblMaxMemory, 2, 3, 0, 1, xpadding=5, ypadding=5)
		self.widgetContainer.attach(txtMaxMemory, 3, 4, 0, 1, xpadding=5, ypadding=5)
		self.widgetContainer.attach(lblTaxonomyFile, 0, 1, 1, 2, xpadding=5, ypadding=5)
		self.widgetContainer.attach(txtTaxonomyFile, 1, 2, 1, 2, xpadding=5, ypadding=5)
		self.widgetContainer.attach(lblSeqFile, 2, 3, 1, 2, xpadding=5, ypadding=5)
		self.widgetContainer.attach(txtSeqFile, 3, 4, 1, 2, xpadding=5, ypadding=5)
		return self.widgetContainer, label

class TaxaPlot(Analysis):
	def __init__(self):
		Analysis.__init__(self)
		self.once = True
		self.XMLName = "taxaplot"
		
		
	def construct_widgets(self):
		#No widgets required
		label = "Make bar and area charts of the taxa using QIIME."
		return self.widgetContainer, label

class Uchime(Analysis):
	def __init__(self):
		Analysis.__init__(self)
		self.once = True
		self.XMLName = "uchime"
		
		
	def construct_widgets(self):
		self.widgetContainer = gtk.Table(2,1)
		label = "Do  chimera  checking  with  UCHIME. Since the parameters \
vary based on the type of DNA, you can specify certain profile to be used."
		lblProfile = gtk.Label("Profile:")
		cmbProfile = gtk.combo_box_new_text()
		cmbProfile.append_text("v3-stringent")
		cmbProfile.append_text("v3-relaxed")
		self.widgetInfo.append((cmbProfile, "ComboBoxText", False, "profile"))
		self.widgetContainer.attach(lblProfile, 0, 1, 0, 1, xpadding=5, ypadding=5)
		self.widgetContainer.attach(cmbProfile, 1, 2, 0, 1, yoptions=gtk.SHRINK, xpadding=5, ypadding=5)
		return self.widgetContainer, label

class UnifracMRPP(Analysis):
	def __init__(self):
		Analysis.__init__(self)
		self.once = True
		self.XMLName = "unifrac-mrpp"
		
		
	def construct_widgets(self):
		self.widgetContainer = gtk.Table(2,1)
		label = "Compute  Multi Response Permutation Procedure of \
within-versus among-group dissimilarities in R using Unifrac \
distances as provided by QIIME's beta diversity script. Library \
is rarefied to the specified size, or if size is set to auto, \
it will rarefy to the smallest sample size. If no size is \
specified, no rarefaction will occur (which is probably wrong)."
		lblSize = gtk.Label("Size:")
		txtSize = gtk.Entry()
		self.widgetInfo.append((txtSize, "Entry", False, "size"))
		self.widgetContainer.attach(lblSize, 0, 1, 0, 1, xpadding=5, ypadding=5)
		self.widgetContainer.attach(txtSize, 1, 2, 0, 1, xpadding=5, ypadding=5)
		return self.widgetContainer, label
	
def create_analysis(wm, analysis_string):
	### This function is given a string containing the analysis name
	# it returns a container widget containing all of the necesarry
	# widgets to collect properties for the analysis, and a string that
	# describes the analysis and its properties
	
	if ( analysis_string == "Alpha Diversity"):
		analysis = AlphaDiv()
	elif ( analysis_string == "Beta Diversity"):
		analysis = BetaDiv()
	elif ( analysis_string == "BLAST DB Creation" ):
		analysis = BLAST()
	elif ( analysis_string == "Compare Libraries" ):
		analysis = CompareLibs()
	elif ( analysis_string == "Indicator Species" ):
		analysis = Duleg()
	elif ( analysis_string == "Heatmap" ):
		analysis = Heatmap()
	elif ( analysis_string == "Jackknifed Beta Diversity" ):
		analysis = Jackknife()
	elif ( analysis_string == "MRPP" ):
		analysis = MRPP()
	elif ( analysis_string == "NMF"):
		analysis = NMF()
	elif ( analysis_string == "NMF Concordance"):
		analysis = NMFConcordance()
	elif ( analysis_string == "NMF Auto"):
		analysis = NMFAuto()
	elif ( analysis_string == "PCoA"):
		analysis = PCoA()
	elif ( analysis_string == "Rank Abundance Curve" ):
		analysis = RankAbundance()
	elif ( analysis_string == "RDP Configuration" ):
		analysis = RDP()
	elif ( analysis_string == "Taxonomy Plot" ):
		analysis = TaxaPlot()
	elif ( analysis_string == "Uchime Chimera Analysis" ):
		analysis = Uchime()
	elif ( analysis_string == "Unifrac MRPP" ):
		analysis = UnifracMRPP()
	else:
		analysis = None
		
	if ( analysis == None ):
		container = None
		label = "Select an analysis from the dropdown."
	else:
		wm.ConstructedAnalysis = analysis
		container, label = analysis.construct_widgets()
	
	if ( container != None ):
		container.set_border_width(10)
		
	return container, label
	
def error_dialogue(label):
	lblError = gtk.Label(label)
	dialog = gtk.Dialog("AXIOME: Error", None, gtk.DIALOG_MODAL | \
	gtk.DIALOG_DESTROY_WITH_PARENT, (gtk.STOCK_OK, gtk.RESPONSE_OK))
	dialog.get_content_area().pack_start(lblError, True, True, 25)
	lblError.show()
	dialog.run()
	dialog.destroy()

class WindowManager(object): 

	### Main Window ###
		
	def on_btnBegin_clicked(self, widget):
		if (self.DefineMetadata == None):
			self.builder.add_from_file(determine_path() + "/res/DefineMetadata.ui")
			self.builder.connect_signals(self)
			self.DefineMetadata = self.builder.get_object("axiome_define_metadata")
			self.mainWindow.hide()
			self.DefineMetadata.show()
		else:
			self.DefineMetadata.show()
			
	### Step 1: Define Metadata ###
			
	def on_btnNext1_clicked(self, widget):
		if (self.DefineSourceFiles == None):
			self.builder.add_from_file(determine_path() + "/res/DefineSourceFiles.ui")
			self.builder.connect_signals(self)
			self.DefineSourceFiles = self.builder.get_object("axiome_define_source_files")
			self.DefineMetadata.hide()
			self.DefineSourceFiles.show()
		else:
			self.DefineMetadata.hide()
			self.DefineSourceFiles.show()
			
	def on_btnMetadataAdd_clicked(self, treeview):
		model = treeview.get_model()
		names = list()
		
		for row in model:
			names.append(row[0])
		
		#Add only a unique name to the list
		i = 1
		while True:
			needle = "New" + str(i)
			if ( not needle in names ):
				break
			i += 1
				
		model.append((needle,"String"))
		
	def on_btnMetadataRemove_clicked(self, treeview):
		model = treeview.get_model()
		selection = treeview.get_selection()
		selectedrow = selection.get_selected()[1]
		model.remove(selectedrow)
		
	def on_rendMetadataName_edited(self, textrenderer, path, new_text):
		if new_text[0].isalpha():
			treeview = self.builder.get_object("treMetadata")
			model = treeview.get_model()
			selectedrow = model.get_iter(path)
			model.set(selectedrow, 0, new_text)
		else:
			error_dialogue("Metadata names must start with a letter.")
		
	def on_cmbMetadataType_changed(self, combo, path, new_iter):
		treeview = self.builder.get_object("treMetadata")
		model = treeview.get_model()
		selectedrow = model.get_iter(path)
		combomodel = self.builder.get_object("lstType")
		new_text = combomodel.get_value(new_iter, 0)
		model.set(selectedrow, 1, new_text)
		
			
	### Step 2: Define Source Files ###
			
	def on_btnAddSource_clicked(self, widget):
		self.DefineSourceFiles.hide()
		self.builder.get_object("axiome_select_file_format").show()
		
	def on_btnRemoveSource_clicked(self, treeview):
		model = treeview.get_model()
		selection = treeview.get_selection()
		selectedrow = selection.get_selected()[1]
		model.remove(selectedrow)
		
	def on_btnEditSource_clicked(self, treeview):
		selection = treeview.get_selection()
		selected = selection.get_selected()
		selectedrow = selected[1]
		model = selected[0]
		
		filetype = model.get_value(selectedrow, 0)

		if (filetype == "FASTA"):
			self.Editing = selected
			self.builder.get_object("txtFastaPath").set_text(model.get_value(selectedrow, 1))
			self.DefineSourceFiles.hide()
			self.builder.get_object("axiome_fasta").show()
		elif (filetype == "PANDA"):
			self.Editing = selected
			self.builder.get_object("txtFastqFwd").set_text(model.get_value(selectedrow, 1))
			self.builder.get_object("txtFastqRev").set_text(model.get_value(selectedrow, 2))
			self.builder.get_object("txtFwdPrimer").set_text(model.get_value(selectedrow, 3))
			self.builder.get_object("txtRevPrimer").set_text(model.get_value(selectedrow, 4))
			self.builder.get_object("txtQualityThresh").set_text(model.get_value(selectedrow, 5))
			self.builder.get_object("cmbFastqVers").set_active(model.get_value(selectedrow, 6))
			self.DefineSourceFiles.hide()
			self.builder.get_object("axiome_fastq_panda").show()
		else:
			print("Error: Unrecognized type selected for editing")
		
	### Source File Format Selection ###
		
	def on_btnFormatCancel_clicked(self, window):
		window.hide()
		self.DefineSourceFiles.show()
		
	def on_btnFasta_clicked(self, window):
		window.hide()
		FilePathInput = self.builder.get_object("txtFastaPath")
		FilePathInput.set_text("")
		FilePathInput.grab_focus()
		fastaWindow = self.builder.get_object("axiome_fasta").show()
		
	def on_btnFastq_clicked(self, window):
		window.hide()
		entries = ["txtFastqFwd","txtFastqRev","txtFwdPrimer","txtRevPrimer","txtQualityThresh"]
		for item in entries:
			self.builder.get_object(item).set_text("")
		self.builder.get_object("txtFastqFwd").grab_focus()
		self.builder.get_object("cmbFastqVers").set_active(5)
		self.builder.get_object("axiome_fastq_panda").show()
		
	def on_btnSourceBack_clicked(self,widget):
		self.DefineSourceFiles.hide()
		self.DefineMetadata.show()
		
	def on_btnSourceNext_clicked(self, window):
		source_list = self.builder.get_object("lstSourceInfo")
		if len(source_list) == 0:
			error_dialogue("At least one source file must be specified.")
		else:
			if (self.DefineSamples == None):
				self.builder.add_from_file(determine_path() + "/res/DefineSamples.ui")
				self.builder.connect_signals(self)
				self.DefineSamples = self.builder.get_object("axiome_define_samples")
			metadatamodel = self.builder.get_object("lstMetadata")
			treeview = self.builder.get_object("treSampleData")
			colindex = 0	
			for row in metadatamodel:
				colindex += 1
				rend = gtk.CellRendererText()
				rend.set_property("editable", True)
				rend.connect("edited", self.on_sample_data_edited, colindex)
				col = gtk.TreeViewColumn(row[0], rend)
				col.add_attribute(rend, "text", colindex)
				treeview.append_column(col)
			filelist = self.builder.get_object("lstSourceInfo")
			self.SampleData = list()
			for filename in filelist:
				self.SampleData.append(gtk.ListStore(*[gobject.TYPE_STRING]*(colindex+1)))
			treeview.set_model(self.SampleData[0])
			numfiles = len(filelist)
			colHeader = self.builder.get_object("colID")
			if filelist[0][0].lower() == "fasta":
				colHeader.set_title("Regex")
			step3label = self.builder.get_object("lblStep3")
			filenamelabel = self.builder.get_object("lblSampleFilename")
			step3label.set_label("Step 3: Define Samples (File 1 of " + str(numfiles) + ")")
			filenamelabel.set_label("Filename: " + filelist[0][1])
			self.DefineSourceFiles.hide()
			self.DefineSamples.show()
		
	### Format Definition Windows ###
	
	def close_to_select_format(self, window):
		window.hide()
		#If we are editing, go back to the main window (and cancel editing)
		if (self.Editing != None):
			self.Editing = None
			self.DefineSourceFiles.show()
		#If we aren't editing, go back to source format selection
		else:
			self.builder.get_object("axiome_select_file_format").show()
			
		
	def on_btnFastaOK_clicked(self, window):
		model = self.builder.get_object("lstSourceInfo")
		filepath = self.builder.get_object("txtFastaPath").get_text()
		
		#TODO: Warn if filepath is blank
		
		#List model stores (Type, FWD Path, REV Path, Fwd Primer,
		# REV Primer, Quality Threshold, Version)
		#Only two of these are used for FASTA files
		if (filepath == None) | (filepath == ""):
			error_dialogue("File Path must be provided.")
		else:
			if (self.Editing != None):
				model.set(self.Editing[1], 0, "FASTA", 1, filepath)
				self.Editing = None
			else:
				newrow = model.append()
				model.set(newrow, 0, "FASTA", 1, filepath)
				
			window.hide()
			self.DefineSourceFiles.show()
		
	def on_btnFastqOK_clicked(self, window):
		model = self.builder.get_object("lstSourceInfo")
		fwdfilepath = self.builder.get_object("txtFastqFwd").get_text()
		revfilepath = self.builder.get_object("txtFastqRev").get_text()
		fwdprimer = self.builder.get_object("txtFwdPrimer").get_text()
		revprimer = self.builder.get_object("txtRevPrimer").get_text()
		quality = self.builder.get_object("txtQualityThresh").get_text()
		casava_version = self.builder.get_object("cmbFastqVers").get_active()
		
		if (fwdfilepath == None) | (fwdfilepath == "") | \
		(revfilepath == None) | (revfilepath == ""):
			error_dialogue("Forward and Reverse file paths must be provided.")
		else:
			#List model stores (Type, FWD Path, REV Path, Fwd Primer,
			# REV Primer, Quality Threshold, Version)
			#Only two of these are used for FASTA files
			if (self.Editing != None):
				model.set(self.Editing[1], 0, "PANDA", 1, fwdfilepath, 2, revfilepath, 3, fwdprimer, 4, revprimer, 5, quality, 6, str(casava_version))
				self.Editing = None
			else:
				model.append(("PANDA", fwdfilepath, revfilepath, fwdprimer, revprimer, quality, str(casava_version)))
			
			window.hide()
			self.DefineSourceFiles.show()
		
	def on_txtFastqFwd_changed(self, widget):
		label = self.builder.get_object("lblFastqFwd")
		if ( widget.get_text() == "" ):
			label.set_markup("<span color=\"#FF0000\">Forward File Path:</span>")
		else:
			label.set_markup("<span color=\"#000000\">Forward File Path:</span>")
		
	def on_txtFastqRev_changed(self, widget):
		label = self.builder.get_object("lblFastqRev")
		if ( widget.get_text() == "" ):
			label.set_markup("<span color=\"#FF0000\">Reverse File Path:</span>")
		else:
			label.set_markup("<span color=\"#000000\">Reverse File Path:</span>")
			
	### Step 3: Define Samples ###
	
	def on_btnSampleAdd_clicked(self, treeview):
		listmodel = treeview.get_model()
		listmodel.append()
		
	def on_btnSampleRemove_clicked(self, treeview):
		model = treeview.get_model()
		selection = treeview.get_selection()
		selectedrow = selection.get_selected()[1]
		model.remove(selectedrow)
		
	def on_sample_data_edited(self, textrenderer, path, new_text, colindex=0):
		selectedrow = self.SampleData[self.SampleFileIndex].get_iter(path)
		self.SampleData[self.SampleFileIndex].set(selectedrow, colindex, new_text)
	
	def update_sample_display(self):
			treeview = self.builder.get_object("treSampleData")
			filelist = self.builder.get_object("lstSourceInfo")
			treeview.set_model(self.SampleData[self.SampleFileIndex])
			step3label = self.builder.get_object("lblStep3")
			filenamelabel = self.builder.get_object("lblSampleFilename")
			step3label.set_label("Step 3: Define Samples (File " + str(self.SampleFileIndex + 1) + " of " + str(len(filelist)) + ")")
			filenamelabel.set_label("Filename: " + filelist[self.SampleFileIndex][1])
			colHeader = self.builder.get_object("colID")
			if filelist[self.SampleFileIndex][0].lower() == "fasta":
				colHeader.set_title("Regex")
			elif filelist[self.SampleFileIndex][0].lower() == "panda":
				colHeader.set_title("Tag")
		
	def on_btnSampleBack_clicked(self, widget):
		if (self.SampleFileIndex == 0):
			lblError = gtk.Label("Going back will erase all input metadata.\nContinue?")
			lblError.set_justify(gtk.JUSTIFY_CENTER)
			dialog = gtk.Dialog("AXIOME: Back?", None, gtk.DIALOG_MODAL | \
			gtk.DIALOG_DESTROY_WITH_PARENT, (gtk.STOCK_YES, gtk.RESPONSE_YES, gtk.STOCK_NO, gtk.RESPONSE_NO))
			dialog.get_content_area().pack_start(lblError, True, True, 25)
			lblError.show()
			response = dialog.run()
			dialog.destroy()
			if response == gtk.RESPONSE_YES:
				self.DefineSamples.hide()
				self.DefineSourceFiles.show()
				return False
			else:
				return True
		else:
			self.SampleFileIndex -= 1
			self.update_sample_display()

	def on_btnSampleNext_clicked(self, treeview):
		data_list = treeview.get_model()
		emptyfield = False
		for row in data_list:
			for item in row:
				if (item == None) | (item == ""):
					emptyfield = True
		if len(data_list) == 0:
			error_dialogue("Source file must have at least one sample.")
		elif emptyfield:
			error_dialogue("One or more metadata fields empty.\nAll fields must be filled.")
		else:
			if ((self.SampleFileIndex +1) < len(self.SampleData)):
				self.SampleFileIndex += 1
				self.update_sample_display()
			else:
				if (self.DefineAnalyses == None):
					self.builder.add_from_file(determine_path() + "/res/DefineAnalyses.ui")
					self.builder.connect_signals(self)
					self.DefineAnalyses = self.builder.get_object("axiome_define_analyses")
					#Set up the QIIME analysis as default
					cmbPipeline = self.builder.get_object("cmbPipeline")
					cmbQOTU = self.builder.get_object("cmbQOTU")
					cmbQAlign = self.builder.get_object("cmbQAlign")
					cmbQPhylo = self.builder.get_object("cmbQPhylo")
					cmbMOTU = self.builder.get_object("cmbMOTU")
					cmbQOTU.set_active(7)
					cmbQAlign.set_active(2)
					cmbQPhylo.set_active(0)
					cmbMOTU.set_active(0)
					cmbPipeline.set_active(0)
				self.DefineSamples.hide()
				self.DefineAnalyses.show()
		
	### Step 4: Define Methods and Analyses ###
	
	def on_cmbPipeline_changed(self, widget):
		#box = self.builder.get_object("boxAnalysesMain")
		#if self.PipelineContainer != None:
			#box.remove(self.PipelineContainer)
		cmbAnalyses = self.builder.get_object("cmbAnalyses")
		if widget.get_active_text() == "QIIME":
			qiimeanalyses = ["Alpha Diversity", "Beta Diversity", "BLAST DB Creation", \
			"Compare Libraries", "Heatmap", "Indicator Species", "Jackknifed Beta Diversity", \
			"MRPP", "NMF", "NMF Concordance", "NMF Auto", "PCoA", "Rank Abundance Curve", \
			"RDP Configuration", "Taxonomy Plot", "Uchime Chimera Analysis", "Unifrac MRPP"]
			cmbAnalyses.get_model().clear()
			for analysis in qiimeanalyses:
				cmbAnalyses.append_text(analysis)
			self.builder.get_object("grdMothur").set_visible(False)
			self.builder.get_object("grdQIIME").set_visible(True)
		elif widget.get_active_text() == "mothur":
			mothuranalyses = ["Alpha Diversity", "Indicator Species", "MRPP", \
			"NMF", "NMF Concordance", "NMF Auto", "PCoA", "Taxonomy Plot"]
			cmbAnalyses.get_model().clear()
			for analysis in mothuranalyses:
				cmbAnalyses.append_text(analysis)
			self.builder.get_object("grdMothur").set_visible(True)
			self.builder.get_object("grdQIIME").set_visible(False)
	
	def on_cmbQOTU_changed(self, widget):
		txtQOTURefSeqs = self.builder.get_object("txtQOTURefSeqs")
		txtQOTUBlastDB = self.builder.get_object("txtQOTUBlastDB")
		lblQOTURefSeqs = self.builder.get_object("lblQRefSeqs")
		lblQOTUBlastDB = self.builder.get_object("lblQBlastDB")
		if (widget.get_active_text() == "usearch_ref") | (widget.get_active_text() == "uclust_ref"):
			txtQOTURefSeqs.set_sensitive(True)
			txtQOTUBlastDB.set_sensitive(False)
			lblQOTURefSeqs.set_sensitive(True)
			lblQOTUBlastDB.set_sensitive(False)
		elif (widget.get_active_text() == "blast"):
			txtQOTURefSeqs.set_sensitive(True)
			txtQOTUBlastDB.set_sensitive(True)
			lblQOTURefSeqs.set_sensitive(True)
			lblQOTUBlastDB.set_sensitive(True)
		else:
			txtQOTURefSeqs.set_sensitive(False)
			txtQOTUBlastDB.set_sensitive(False)
			lblQOTURefSeqs.set_sensitive(False)
			lblQOTUBlastDB.set_sensitive(False)
		
	def on_btnAnalysisAdd_clicked(self, window):
		self.builder.get_object("cmbAnalyses").set_active(-1)
		window.resize(275,200)
		width, height = window.get_size()
		window.move((gtk.gdk.screen_width() - width)/2, (gtk.gdk.screen_height() - height)/2)
		window.show()
		
	def on_btnAnalysisRemove_clicked(self, treeview):
		model = treeview.get_model()
		selection = treeview.get_selection()
		selectedrow = selection.get_selected()[1]
		model.remove(selectedrow)
		
	def on_cmbAnalyses_changed(self, box):
		if (self.PropContainer != None):
			box.remove(self.PropContainer)
		combo = self.builder.get_object("cmbAnalyses")
		infolabel = self.builder.get_object("lblAnalInfo")
		box2 = self.builder.get_object("boxAnalysisMain")
		container, label = create_analysis(self, combo.get_active_text())
		self.PropContainer = container
		if (container != None):
			box.pack_start(container, True, True, 0)
			box.reorder_child(container, 3)
			container.show_all()
		infolabel.set_text(label)
		#Recenter window
		window = self.builder.get_object("axiome_analysis_addition")
		#width, height = window.get_size()
		#window.move((gtk.gdk.screen_width() - width)/2, (gtk.gdk.screen_height() - height)/2)
		window.resize(1,1)

	def duplicate_analysis(self, analysis, model):
		for row in model:
			if (row[0] == analysis):
				return True
		return False

	def on_btnAnalysisAddOK_clicked(self, window):
		model = self.builder.get_object("lstAnalyses")
		lblAnalWarning = self.builder.get_object("lblAnalWarning")
		errordialog = self.builder.get_object("analysis_warning")
		if self.ConstructedAnalysis.is_only_once() & self.duplicate_analysis(self.ConstructedAnalysis.get_xml_name(), model):
			lblAnalWarning.set_text("Analysis already present. Only one analysis of this type is allowed.")
			errordialog.run()
		#Check if any fields are blank
		elif ( self.ConstructedAnalysis.required_fields_empty() ):
			lblAnalWarning.set_text("A required field is empty. Please fill in all required fields (denoted with red text).")
			errordialog.run()
		else:
			model.append((self.ConstructedAnalysis.get_xml_name(), self.ConstructedAnalysis.get_parameter_string()))
			window.hide()
			
		
	def on_btnAnalysisAddCancel_clicked(self, window):
		self.ConstructedAnalysis = None
		window.hide()
		
	def on_btnEmptyWarningOK_clicked(self, dialogue):
		dialogue.hide()
		
	def on_chkMultiCore_toggled(self, checkbox):
		self.builder.get_object("lblNumCores").set_sensitive(checkbox.get_active())
		self.builder.get_object("spnNumCores").set_sensitive(checkbox.get_active())
		
	def on_btnAnalysesBack_clicked(self, widget):
		self.DefineAnalyses.hide()
		self.DefineSamples.show()
	
	def on_btnLaunchSave_clicked(self, savedialog):
		chooser = gtk.FileChooserDialog(title="Save File",action=gtk.FILE_CHOOSER_ACTION_SAVE, \
			buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK))
		chooser.set_default_response(gtk.RESPONSE_OK)
		chooser.set_filter(self.builder.get_object("ftrAx"))
		chooser.set_do_overwrite_confirmation(True)
		response = chooser.run()
		if response == gtk.RESPONSE_OK:
			print chooser.get_filename(), 'selected'
			self.save_session(chooser.get_filename())
			chooser.destroy()
			print "File saved! Exiting..."
			gtk.main_quit()
		else:
			chooser.destroy()
		
	### Generate XML File ###
	
	def get_pipeline_string(self):
		pipeline = self.builder.get_object("cmbPipeline").get_active_text()
		outstring = "<axiome version=\"1.6\" "
		
		if pipeline == "QIIME":
			outstring = outstring + "pipeline=\"qiime\" "
			alignmethod = self.builder.get_object("cmbQAlign").get_active_text()
			phylomethod = self.builder.get_object("cmbQPhylo").get_active_text()
			otumethod = self.builder.get_object("cmbQOTU").get_active_text()
			clusteridentity = str(self.builder.get_object("spnQCluster").get_value())
			otuflags = self.builder.get_object("txtQOTUFlags").get_text()
			oturefseqs = self.builder.get_object("txtQOTURefSeqs").get_text()
			otublastdb = self.builder.get_object("txtQOTUBlastDB").get_text()
			verbose = str(self.builder.get_object("chkQVerbose").get_active())
			items = [alignmethod, phylomethod, otumethod, clusteridentity, \
			otuflags, oturefseqs, otublastdb, verbose]
			labels = ["align-method", "phylogeny-method", "otu-method", \
			"cluster-identity", "otu-flags", "otu-refseqs", "otu-blastdb", "verbose"]

		elif pipeline == "mothur":
			outstring = outstring + "pipeline=\"mothur\" "
			otumethod = self.builder.get_object("cmbMOTU").get_active_text()
			clusteridentity = str(self.builder.get_object("spnMCluster").get_value())
			classseqs = self.builder.get_object("txtMClassSeqs").get_text()
			classtaxa = self.builder.get_object("txtMClassTaxa").get_text()
			aligntemplate = self.builder.get_object("txtMAlign").get_text()
			verbose = str(self.builder.get_object("chkQVerbose").get_active())
			items = [otumethod, clusteridentity, classseqs, classtaxa, \
			aligntemplate, verbose]
			labels = ["otu-method", "cluster-identity", "classification-sequences", \
			"classification-taxonomy", "alignment-template", "verbose"]
			
		i = 0
		for item in items:
			if (item != None) & (item != ""):
				outstring = outstring + labels[i] + "=\"" + item + "\" "
			i += 1
		outstring = outstring + ">\n\n"
		return outstring
	
	
	def add_axiome_tag(self):
		self.XMLOutput = "<?xml version=\"1.0\"?>\n<!-- Generated by AXIOMATIC v 0.1 -->\n"
		self.XMLOutput += self.get_pipeline_string()
		
	def add_definitions(self):
		self.MetadataLabels = list()
		def_list = self.builder.get_object("lstMetadata")
		for row in def_list:
			self.MetadataLabels.append(row[0])
			self.XMLOutput += "\t<def name=\"" + row[0] + "\" type=\"" + row[1].lower()[0] + "\"/>\n"
		self.XMLOutput += "\n"
			
	def add_samples(self):
		source_list = self.builder.get_object("lstSourceInfo")
		i = 0
		for row in source_list:
			if row[0].lower() == "fasta":
				self.XMLOutput += "\t<fasta file=\"" + row[1] + "\">\n"
				searchterm = "regex"
			elif row[0].lower() == "panda":
				self.XMLOutput += "\t<panda forward=\"" + row[1] + "\" reverse=\"" \
				+ row[2] + "\" version=\"" + self.builder.get_object("cmbFastqVers").get_model()[row[6]][0] + "\""
				if (row[3] != None) & (row[3] != ""):
					self.XMLOutput += " fprimer=\"" + row[3] + "\""
				if (row[4] != None) & (row[4] != ""):
					self.XMLOutput += " rprimer=\"" + row[4] + "\""
				if (row[5] != None) & (row[5] != ""):
					self.XMLOutput += " threshold=\"" + row[5] + "\""
				self.XMLOutput += ">\n"
				searchterm = "tag"
			for sample in self.SampleData[i]:
				self.XMLOutput += "\t\t<sample " + searchterm + "=\"" + sample[0] + "\""
				j = 1
				for label in self.MetadataLabels:
					if sample[j] != None:
						self.XMLOutput += " " + label + "=\"" + sample[j] + "\""
					j += 1
				self.XMLOutput += "/>\n"
			self.XMLOutput += "\t</" + row[0].lower() + ">\n\n"
			i += 1
			
	def add_analyses(self):
		analysis_list = self.builder.get_object("lstAnalyses")
		#First, check for multicore
		if self.builder.get_object("chkMultiCore").get_active():
			num_cores = self.builder.get_object("spnNumCores").get_value()
			self.XMLOutput += "\t<multicore num-cores=\"" + str(int(num_cores)) + "\"/>\n"
		for row in analysis_list:
			self.XMLOutput += "\t<" + row[0] + row[1] + "/>\n"
			
		self.XMLOutput += "\n</axiome>"
		
	def save_session(self, filepath):
		ax = gio.File(path=filepath)
		self.add_axiome_tag()
		self.add_definitions()
		self.add_samples()
		self.add_analyses()
		ax.replace_contents(self.XMLOutput, None, False, gio.FILE_CREATE_NONE, None)
		


	### Generic ###
		
	def on_close(self, window, event=None):
		lblError = gtk.Label("Are you sure you want to quit?\nAll changes will be lost.")
		lblError.set_justify(gtk.JUSTIFY_CENTER)
		dialog = gtk.Dialog("AXIOME: Quit?", None, gtk.DIALOG_MODAL | \
		gtk.DIALOG_DESTROY_WITH_PARENT, (gtk.STOCK_YES, gtk.RESPONSE_YES, gtk.STOCK_NO, gtk.RESPONSE_NO))
		dialog.get_content_area().pack_start(lblError, True, True, 25)
		lblError.show()
		response = dialog.run()
		dialog.destroy()
		if response == gtk.RESPONSE_YES:
			gtk.main_quit()
			return False
		else:
			return True
		
	def __init__(self):
	    self.builder = gtk.Builder()
	    self.builder.add_from_file(determine_path() + "/res/AxiomeUiWindow.ui")
	    self.builder.connect_signals(self)
	    self.mainWindow = self.builder.get_object("axiome_ui_window")
	    self.DefineMetadata = None
	    self.MetadataLabels = None
	    self.DefineSourceFiles = None
	    self.DefineSamples = None
	    self.DefineAnalyses = None
	    self.SampleData = None
	    self.Editing = None
	    self.PropContainer = None
	    self.ConstructedAnalysis = None
	    self.SampleFileIndex = 0
	    self.XMLOutput = None
	    self.mainWindow.show()
	    
def main():
	mainWindow = WindowManager()
	gtk.main()

if __name__ == '__main__':
	main()
