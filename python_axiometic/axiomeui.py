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

import pygtk, os, sys
pygtk.require("2.0")
import gtk, gobject, gio
from xml.dom.minidom import parse

class XMLFile:
	def __init__(self, path):
		self.File = parse(path)
		
	def getNextSibling(self, node):
		if (node.nextSibling != None):
			return node.nextSibling
		else:
			return None
		
class analysisDefs(XMLFile):
	
	def getAnalysisList(self):
		pipe_analysis_dict = {}
		#Skip the outermost <plugin> tag, go in to the plugins
		node = self.File.firstChild.firstChild
		while node != None:
			if node.nodeType == 1:
				for element in node.getElementsByTagName("pipeline"):
					attribs = element.attributes
					if attribs != None:
						for i in range(0, attribs.length):
							pipeline = attribs.item(i).name
							logical = attribs.item(i).value
							if logical.lower() == "true":
								if not(pipe_analysis_dict.has_key(pipeline)):
									pipe_analysis_dict[pipeline]=list()
								pipe_analysis_dict[pipeline].append(node.nodeName)
			node = node.nextSibling
		return pipe_analysis_dict
		
	def __init__(self, path):
		XMLFile.__init__(self, path)
		self.pipe_analysis_dict = self.getAnalysisList()
		self.currentWidgets = None
	
	def analysis_node_search(self, analysis):
		elems = self.File.getElementsByTagName(analysis)
		if elems.length > 1:
			print "ERROR: More than one definition for analysis \"" + analysis + "\" found in plugin_defs.xml. Using first definition in file."
		elif elems.length == 0:
			print "ERROR: Analysis \"" + str(analysis) + "\" not found. Please check plugin_defs.xml."
		node = elems.item(0)
		return node
		
	def pipeline_node_search(self, analysis, pipeline):
		node = self.analysis_node_search(analysis)
		#Look for the pipeline definition for the analysis
		pipenodelist = node.getElementsByTagName("pipeline")
		for i in range(0, pipenodelist.length):
			if pipenodelist.item(i).hasAttribute(pipeline):
				pipenode = pipenodelist.item(i)
		return pipenode
		
	def is_only_once(self, analysis, pipeline):
		analysisnode = self.analysis_node_search(analysis)
		once = analysisnode.getAttribute("once")
		if once.lower() == "true":
			return True
		else:
			return False
		
	def createListWidget(self, node):
		box = gtk.HBox()
		labeltext = node.getAttribute("label")
		label = gtk.Label(labeltext)
		box.pack_start(label)
		combo = gtk.combo_box_new_text()
		itemnodes = node.getElementsByTagName("item")
		defaultnodes = node.getElementsByTagName("default")
		if defaultnodes.length != 0:
			default = defaultnodes.item(0).firstChild.nodeValue
		else:
			default = None
		for i in range(0, itemnodes.length):
			itemtext = itemnodes.item(i).firstChild.nodeValue
			combo.append_text(itemtext)
			if itemtext == default:
				combo.set_active(i)
		box.pack_start(combo)
		return box, combo, label
		
	def createEntryWidget(self, node):
		box = gtk.HBox()
		labeltext = node.getAttribute("label")
		label = gtk.Label(labeltext)
		box.pack_start(label)
		entry = gtk.Entry()
		defaultnodes = node.getElementsByTagName("default")
		if defaultnodes.length != 0:
			default = defaultnodes.item(0).firstChild.nodeValue
			entry.set_text(default)
		box.pack_start(entry)
		return box, entry, label
		
	def createFloatWidget(self, node):
		box = gtk.HBox()
		labeltext = node.getAttribute("label")
		label = gtk.Label(labeltext)
		box.pack_start(label)
		defaultnodes = node.getElementsByTagName("default")
		if defaultnodes.length == 1:
			default = float(defaultnodes.item(0).firstChild.nodeValue)
		minnodes = node.getElementsByTagName("min")
		if minnodes.length == 1:
			minnum = float(minnodes.item(0).firstChild.nodeValue)
		maxnodes = node.getElementsByTagName("max")
		if maxnodes.length == 1:
			maxnum = float(maxnodes.item(0).firstChild.nodeValue)
		precisionnodes = node.getElementsByTagName("precision")
		if precisionnodes.length == 1:
			precision = int(precisionnodes.item(0).firstChild.nodeValue)
			if precision == 0:
				precision = 2
		adjust = gtk.Adjustment(default, minnum, maxnum, pow(10, -(precision)))
		spinner = gtk.SpinButton(adjust, climb_rate=1, digits=precision)
		box.pack_start(spinner)
		return box, spinner, label
		
	def createIntWidget(self, node):
		box = gtk.HBox()
		labeltext = node.getAttribute("label")
		label = gtk.Label(labeltext)
		box.pack_start(label)
		defaultnodes = node.getElementsByTagName("default")
		if defaultnodes.length == 1:
			default = int(defaultnodes.item(0).firstChild.nodeValue)
		minnodes = node.getElementsByTagName("min")
		if minnodes.length == 1:
			minnum = int(minnodes.item(0).firstChild.nodeValue)
		maxnodes = node.getElementsByTagName("max")
		if maxnodes.length == 1:
			maxnum = int(maxnodes.item(0).firstChild.nodeValue)
		precisionnodes = node.getElementsByTagName("precision")
		if precisionnodes.length == 1:
			precision = int(precisionnodes.item(0).firstChild.nodeValue)
			if precision == 0:
				precision = 2
		adjust = gtk.Adjustment(default, minnum, maxnum, 1)
		spinner = gtk.SpinButton(adjust, climb_rate=1)
		box.pack_start(spinner)
		return box, spinner, label
		
	def getWidget(self, analysis, pipeline):
		pipenode = self.pipeline_node_search(analysis, pipeline)
		#Get the info label
		infonodelist = pipenode.getElementsByTagName("info")
		if infonodelist.length != 1:
			print "ERROR: " + infonodelist.length + " info definitions found for plugin " + analysis + " with pipeline " + pipeline + ". Should only be one."
		else:
			labeltext = infonodelist.item(0).firstChild.nodeValue
		#Set up a VBox to put all of these widgets in
		mainBox = gtk.VBox()
		#Get the inputs required for the analysis
		inputnodelist = pipenode.getElementsByTagName("input")
		info = list()
		for i in range(0, inputnodelist.length):
			intype = inputnodelist.item(i).getAttribute("type")
			requiredtext = inputnodelist.item(i).getAttribute("required")
			if requiredtext.lower() == "true":
				required = True
			else:
				required = False
			name = inputnodelist.item(i).getAttribute("name")
			if intype == "list":
				box, widget, label = self.createListWidget(inputnodelist.item(i))
				widgettype = "ComboBoxText"
			elif intype == "string":
				box, widget, label = self.createEntryWidget(inputnodelist.item(i))
				widgettype = "Entry"
			elif intype == "float":
				box, widget, label = self.createFloatWidget(inputnodelist.item(i))
				widgettype = "SpinnerFloat"
			elif intype == "integer":
				box, widget, label = self.createIntWidget(inputnodelist.item(i))
				widgettype = "SpinnerInt"
			else:
				print "ERROR: Unrecognized input type \"" + intype + "\"."
				widget = None
			tooltiplist = inputnodelist.item(i).getElementsByTagName("tooltip")
			if tooltiplist.length == 1:
				tooltiptext = tooltiplist.item(0).firstChild.nodeValue
				label.set_tooltip_text(tooltiptext)
			if required:
				label.set_text("<span color=\"#FF0000\">" + label.get_text() + "</span>")
				label.set_use_markup(True)
			info.append((widget, widgettype, required, name))
			mainBox.set_border_width(15)
			mainBox.pack_start(box)
			
		return labeltext, mainBox, info

class AXFile(XMLFile):
	def __init__(self, path, builder):
		try:
			XMLFile.__init__(self, path)
		except:
			error_dialogue("Could not parse .ax file. Please check file.")
			self.Parsed = False
			return
		#Needs access to the Gtk Builder so we can grab the lists
		self.builder = builder
		self.builder.get_object("lstMetadata").clear()
		self.header = self.getHeader()		
		self.processHeader(self.header)
		self.SampleData = list()
		node = self.header.firstChild
		while node != None:
			if node.nodeType == 1:
				if node.nodeName.lower() == "def":
					self.processDef(node)
				elif node.nodeName.lower() == "panda":
					self.processPanda(node)
				elif node.nodeName.lower() == "fasta":
					self.processFasta(node)
				else:
					self.processAnalysis(node)
			node = self.getNextSibling(node)
		self.Parsed = True

	def getHeader(self):
		node = self.File.firstChild
		while node.nodeType != 1:
			node = self.getNextSibling(node)
		return node
			
	def processPanda(self, node):
		print "Adding panda file..."
		fwd = node.getAttribute("forward")
		rev = node.getAttribute("reverse")
		version = node.getAttribute("version")
		fprimer = node.getAttribute("fprimer")
		rprimer = node.getAttribute("rprimer")
		thresh = node.getAttribute("threshold")
		#Add new file to sources list
		sourceslist = self.builder.get_object("lstSourceInfo")
		metadatalist = self.builder.get_object("lstMetadata")
		sourceslist.append(("PANDA", fwd, rev, fprimer, rprimer, thresh, version))
		child = node.firstChild
		#self.SampleData.append(gtk.ListStore(*[gobject.TYPE_STRING]*(len(metadatalist)+1)))
		self.SampleData.append(list())
		while child != None:
			if child.nodeType == 1:
				sampleinfo = {}
				sampleinfo["regextag"] = child.getAttribute("tag")
				for row in metadatalist:
					sampleinfo[row[0]] = child.getAttribute(row[0])
				#sampleliststore =  self.SampleData[len(self.SampleData)-1].append(sampleinfo)
				self.SampleData[len(self.SampleData)-1].append(sampleinfo)
			child = self.getNextSibling(child)
	
	def processFasta(self, node):
		print "Adding fasta file..."
		filename = node.getAttribute("file")
		#Add new file to sources list
		sourceslist = self.builder.get_object("lstSourceInfo")
		metadatalist = self.builder.get_object("lstMetadata")
		newrow = sourceslist.append()
		sourceslist.set(newrow, 0, "FASTA", 1, filename)
		child = node.firstChild
		self.SampleData.append(list())
		while child != None:
			if child.nodeType == 1:
				sampleinfo = {}
				sampleinfo["regextag"] = child.getAttribute("regex")
				for row in metadatalist:
					sampleinfo[row[0]] = child.getAttribute(row[0])
				self.SampleData[len(self.SampleData)-1].append(sampleinfo)
			child = self.getNextSibling(child)
		
	def processDef(self, node):
		lstMetadata = self.builder.get_object("lstMetadata")
		print "Adding metadata: " + node.getAttribute("name") + " Type: " + node.getAttribute("type")
		shorttype = node.getAttribute("type")
		if shorttype.lower() == "i":
			longtype = "Integer"
		elif shorttype.lower() == "d":
			longtype = "Decimal"
		else:
			longtype = "String"
		lstMetadata.append((node.getAttribute("name"), longtype))
		
	
	def processHeader(self, header):
		#Process cluster ID
		cluster = header.getAttribute("cluster-identity")
		if cluster != None:
			self.builder.get_object("adjCluster").set_value(float(cluster))
		pipeline = header.getAttribute("pipeline")
		if pipeline.lower() == "mothur":
			self.builder.get_object("cmbPipeline").set_active(1)
			classseqs = header.getAttribute("classification-sequences")
			self.builder.get_object("txtMClassSeqs").set_text(classseqs)
			classtaxa = header.getAttribute("classification-taxonomy")
			self.builder.get_object("txtMClassTaxa").set_text(classtaxa)
			aligntemplate = header.getAttribute("alignment-template")
			self.builder.get_object("txtMAlign").set_text(aligntemplate)
			otumethod = header.getAttribute("otu-method")
			if (otumethod.lower() == "an") | (otumethod.lower() == "average neighbor") | (otumethod.lower() == "average"):
				self.builder.get_object("cmbMOTU").set_active(0)
			elif (otumethod.lower() == "fn") | (otumethod.lower() == "furthest neighbor") | (otumethod.lower() == "furthest"):
				self.builder.get_object("cmbMOTU").set_active(1)
			elif (otumethod.lower() == "nn") | (otumethod.lower() == "nearest neighbor") | (otumethod.lower() == "nearest"):
				self.builder.get_object("cmbMOTU").set_active(1)
			else:
				self.builder.get_object("cmbMOTU").set_active(0)
			verbosity = header.getAttribute("verbose")
			if (verbosity.lower() == "true") | (verbosity.lower() == "t"):
				self.builder.get_object("chkMVerbose").set_active(True)
		else:
			self.builder.get_object("cmbPipeline").set_active(0)
			verbosity = header.getAttribute("verbose")
			if (verbosity.lower() == "true") | (verbosity.lower() == "t"):
				self.builder.get_object("chkQVerbose").set_active(True)
			align = header.getAttribute("align-method")
			otu = header.getAttribute("otu-method")
			phylo = header.getAttribute("phylogeny-method")
			blastdb = header.getAttribute("otu-blastdb")
			flags = header.getAttribute("otu-flags")
			refseqs = header.getAttribute("otu-refseqs")
			tax = header.getAttribute("classification-method")
			self.builder.get_object("txtQOTUFlags").set_text(flags)
			self.builder.get_object("txtQOTURefSeqs").set_text(refseqs)
			self.builder.get_object("txtQOTUBlastDB").set_text(blastdb)
			phyloindicies = { "fasttree":0, "fast tree":0, "fasttree_v1":1, \
			"raw-fasttree":2, "raw-fasttreemp":3, "fasttreemp":3, "clustalw":4, \
			"clustal":4, "clearcut":5, "raxml":6, "raxml_v730":7, "raxml v730":7, \
			"muscle":8 }
			otuindicies = { "usearch":0, "usearch_ref":1, "usearch-ref":1, \
			"prefix_suffix":2, "prefix-suffix":2, "prefixsuffix":2, "prefix suffix":2, \
			"mothur":3, "trie":4, "blast":5, "uclust_ref":6, "uclust-ref":6, \
			"cdhit":7, "cd-hit":7, "raw-cdhit":8, "raw-cd-hit":8, "uclust":9, \
			"raw-uclust":10 }
			alignindicies = { "infernal":0, "muscle":1, "pynast":2 }
			taxindices = { "rdp":0, "blast":1, "rtax":2 }
			try:
				phyloindex = phyloindicies[phylo]
			except:
				phyloindex = 0
			try:
				otuindex = otuindicies[otu]
			except:
				otuindex = 7
			try:
				alignindex = alignindicies[align]
			except:
				alignindex = 2
			try:
				taxindex = taxindices[tax]
			except:
				taxindex = 0
			self.builder.get_object("cmbQPhylo").set_active(phyloindex)
			self.builder.get_object("cmbQAlign").set_active(alignindex)
			self.builder.get_object("cmbQOTU").set_active(otuindex)
			self.builder.get_object("cmbQTaxMethod").set_active(taxindex)
			
		
	def processAnalysis(self, node):
		#Multi-core is a special case
		if node.nodeName == "multicore":
			numcores = node.getAttribute("num-cores")
			self.builder.get_object("chkMultiCore").set_active(True)
			self.builder.get_object("adjNumCores").set_value(int(numcores))
		#All other analyses processed the same way
		else:
			attributestring = ""
			for i in range(0, node.attributes.length):
				attribute = node.attributes.item(i)
				attributestring += " " + attribute.nodeName + "=\"" + attribute.nodeValue + "\""
			self.builder.get_object("lstAnalyses").append((node.nodeName, attributestring))
		
	def get_sample_data(self):
		return self.SampleData

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
	
	def on_btnOpenAX_file_set(self, widget):
		self.OpenAX = AXFile(widget.get_filename(), self.builder)
		self.SampleData = self.OpenAX.get_sample_data()
		if self.OpenAX.Parsed:
			self.IntroWindow.hide()
			self.DefineMetadata.show()
		else:
			widget.unselect_all()
		
	def on_btnBegin_clicked(self, widget):
		self.IntroWindow.hide()
		self.DefineMetadata.show()
			
	### Step 1: Define Metadata ###
			
	def on_btnNext1_clicked(self, widget):
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
		try:
			selectedrow = selection.get_selected()[1]
			model.remove(selectedrow)
		except:
			pass
		
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
		try:
			selectedrow = selection.get_selected()[1]
			model.remove(selectedrow)
			path = treeview.get_model().get_path(selectedrow)
			del self.SampleData[int(path[0])]
		except:
			pass
		
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
			casava_version = model.get_value(selectedrow, 6)
			casava_dict = { "1.3":0, "1.4":1, "1.5":2, "1.6":3, "1.7":4, "1.8":5 }
			self.builder.get_object("cmbFastqVers").set_active(casava_dict[casava_version])
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
		
	def dict_to_liststore(self, dictlist):
		metadatalist = self.builder.get_object("lstMetadata")
		metaliststore = gtk.ListStore(*[gobject.TYPE_STRING]*(len(metadatalist)+1))
		for i in range(0, len(dictlist)):
			metalist = list()
			metalist.append(dictlist[i]['regextag'])
			for row in metadatalist:
				try:
					data = dictlist[i][row[0]]
				except:
					data = ""
				metalist.append(data)
			metaliststore.append(metalist)
		return metaliststore
		
	def on_btnSourceNext_clicked(self, window):
		source_list = self.builder.get_object("lstSourceInfo")
		if len(source_list) == 0:
			error_dialogue("At least one source file must be specified.")
		else:	
			metadatamodel = self.builder.get_object("lstMetadata")
			treeview = self.builder.get_object("treSampleData")
			colindex = 0	
			colHeader = self.builder.get_object("colID")
			for column in treeview.get_columns():
				treeview.remove_column(column)
			treeview.append_column(colHeader)
			for row in metadatamodel:
				colindex += 1
				rend = gtk.CellRendererText()
				rend.set_property("editable", True)
				rend.connect("edited", self.on_sample_data_edited, colindex)
				col = gtk.TreeViewColumn(row[0], rend)
				col.add_attribute(rend, "text", colindex)
				treeview.append_column(col)
			filelist = self.builder.get_object("lstSourceInfo")
			if self.SampleData == None:
				self.SampleData = list()
				for filename in filelist:
					self.SampleData.append(list())
			treeview.set_model(self.dict_to_liststore(self.SampleData[0]))
			numfiles = len(filelist)
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
				self.SampleData.append(list())
				
			window.hide()
			self.DefineSourceFiles.show()
		
	def on_btnFastqOK_clicked(self, window):
		model = self.builder.get_object("lstSourceInfo")
		fwdfilepath = self.builder.get_object("txtFastqFwd").get_text()
		revfilepath = self.builder.get_object("txtFastqRev").get_text()
		fwdprimer = self.builder.get_object("txtFwdPrimer").get_text()
		revprimer = self.builder.get_object("txtRevPrimer").get_text()
		quality = self.builder.get_object("txtQualityThresh").get_text()
		casava_index = self.builder.get_object("cmbFastqVers").get_active()
		casava_version = self.builder.get_object("lstFastqVersions")[casava_index][0]
		
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
				self.SampleData.append(list())
			
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
		self.SampleData[self.SampleFileIndex].append({})
		
		
	def on_btnSampleRemove_clicked(self, treeview):
		model = treeview.get_model()
		selection = treeview.get_selection()
		try:
			selectedrow = selection.get_selected()[1]
			rownum = model.get_path(selectedrow)[0]
			model.remove(selectedrow)
			del self.SampleData[self.SampleFileIndex][rownum]
		except:
			pass
		
	def on_sample_data_edited(self, textrenderer, path, new_text, colindex=0):
		treeview = self.builder.get_object("treSampleData")
		selectedrow = treeview.get_model().get_iter(path)
		metadataname = treeview.get_column(colindex).get_title()
		if (metadataname == "Regex") | (metadataname == "Tag"):
			metadataname = "regextag"
		self.SampleData[self.SampleFileIndex][int(path)][metadataname] = new_text
		treeview.get_model().set(selectedrow, colindex, new_text)
	
	def update_sample_display(self):
			treeview = self.builder.get_object("treSampleData")
			filelist = self.builder.get_object("lstSourceInfo")
			treeview.set_model(self.dict_to_liststore(self.SampleData[self.SampleFileIndex]))
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
			self.DefineSamples.hide()
			self.DefineSourceFiles.show()
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
			if ((self.SampleFileIndex+1) < len(self.SampleData)):
				self.SampleFileIndex += 1
				self.update_sample_display()
			else:			
				self.DefineSamples.hide()
				self.DefineAnalyses.show()
		
	### Step 4: Define Methods and Analyses ###
	
	def on_cmbPipeline_changed(self, widget):
		#box = self.builder.get_object("boxAnalysesMain")
		#if self.PipelineContainer != None:
			#box.remove(self.PipelineContainer)
		cmbAnalyses = self.builder.get_object("cmbAnalyses")
		if widget.get_active_text() != None:
			analyses = self.pluginDefs.pipe_analysis_dict[widget.get_active_text()]
			cmbAnalyses.get_model().clear()
			for analysis in analyses:
				cmbAnalyses.append_text(analysis)
			if widget.get_active_text() == "qiime":
				self.builder.get_object("grdMothur").set_visible(False)
				self.builder.get_object("grdQIIME").set_visible(True)
			elif widget.get_active_text() == "mothur":
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
		try:
			selectedrow = selection.get_selected()[1]
			model.remove(selectedrow)
		except:
			pass
		
	def on_cmbAnalyses_changed(self, box):
		if (self.PropContainer != None):
			box.remove(self.PropContainer)
		cmbAnalyses = self.builder.get_object("cmbAnalyses")
		infolabel = self.builder.get_object("lblAnalInfo")
		if cmbAnalyses.get_active_text() != None:
			cmbPipeline = self.builder.get_object("cmbPipeline")
			box2 = self.builder.get_object("boxAnalysisMain")
			label, container, info = self.pluginDefs.getWidget(cmbAnalyses.get_active_text(), cmbPipeline.get_active_text())
			self.ConstructedAnalysisInfo = info
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
		else:
			infolabel.set_text("Select an analysis from the dropdown.")

	def duplicate_analysis(self, analysis, model):
		for row in model:
			if (row[0] == analysis):
				return True
		return False
	
	def required_analysis_fields_empty(self):
		#Go through each widget, and, if required, check widget is
		#not empty, using appropriate check for the type
		for widget in self.ConstructedAnalysisInfo:
			if ( widget[2] ):
				if ( widget[1] == "Entry" ):
					if ( widget[0].get_text() == "" ):
						return True
				elif ( widget[1] == "ComboBoxText" ):
					if  ( widget[0].get_active_text() == "" ) | ( widget[0].get_active_text() == None ):
						return True
		return False
		
	def get_analysis_parameter_string(self):
		parameters = ""
		for widget in self.ConstructedAnalysisInfo:
			if ( widget[1] == "Entry" ):
				if ( ( widget[0].get_text() != "" ) & ( widget[0].get_text() != None ) ):
					parameters += " " +  widget[3] + "=\"" + widget[0].get_text() + "\""
			elif ( widget[1] == "ComboBoxText" ):
				if ( ( widget[0].get_active_text() != "" ) & ( widget[0].get_active_text() != None ) ):
					parameters += " " +  widget[3] + "=\"" + widget[0].get_active_text() + "\""
			elif ( widget[1] == "SpinnerInt" ):
				if ( ( widget[0].get_value() != "") & ( widget[0].get_value() != None ) ):
					parameters += " " + widget[3] + "=\"" + str(int(widget[0].get_value())) + "\""
			elif ( widget[1] == "SpinnerFloat" ):
				if ( ( widget[0].get_value() != "") & ( widget[0].get_value() != None ) ):
					parameters += " " + widget[3] + "=\"" + str(widget[0].get_value()) + "\""
		return parameters
	
	def on_btnAnalysisAddOK_clicked(self, window):
		model = self.builder.get_object("lstAnalyses")
		lblAnalWarning = self.builder.get_object("lblAnalWarning")
		errordialog = self.builder.get_object("analysis_warning")
		cmbAnalyses = self.builder.get_object("cmbAnalyses")
		cmbPipeline = self.builder.get_object("cmbPipeline")
		if (self.pluginDefs.is_only_once(cmbAnalyses.get_active_text(), cmbPipeline.get_active_text())) & self.duplicate_analysis(cmbAnalyses.get_active_text(), model):
			lblAnalWarning.set_text("Analysis already present. Only one analysis of this type is allowed.")
			errordialog.run()
		#Check if any fields are blank
		elif ( self.required_analysis_fields_empty() ):
			lblAnalWarning.set_text("A required field is empty. Please fill in all required fields (denoted with red text).")
			errordialog.run()
		else:
			model.append((cmbAnalyses.get_active_text(), self.get_analysis_parameter_string()))
			self.ConstructedAnalysisInfo = None
			window.hide()
			
		
	def on_btnAnalysisAddCancel_clicked(self, window):
		self.ConstructedAnalysisInfo = None
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
		#Get pipeline info
		pipeline = self.builder.get_object("cmbPipeline").get_active_text()
		#For mothur, we require the file locations for the template, classifier seqs, and classifier taxa
		if (pipeline.lower() == "mothur"):
			classseqs = self.builder.get_object("txtMClassSeqs").get_text()
			classtaxa = self.builder.get_object("txtMClassTaxa").get_text()
			aligntemplate = self.builder.get_object("txtMAlign").get_text()
			if (classtaxa == "") | (classtaxa == None):
				error_dialogue("Classification Taxonomy file location must be provided.")
				return
			elif (classseqs == "") | (classseqs == None):
				error_dialogue("Classification Sequences file location must be provided.")
				return
			elif (aligntemplate == "") | (aligntemplate == None):
				error_dialogue("Alignment Template file location must be provided.")
				return
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
		
		if pipeline == "qiime":
			outstring = outstring + "pipeline=\"qiime\" "
			alignmethod = self.builder.get_object("cmbQAlign").get_active_text()
			phylomethod = self.builder.get_object("cmbQPhylo").get_active_text()
			taxmethod = self.builder.get_object("cmbQTaxMethod").get_active_text()
			otumethod = self.builder.get_object("cmbQOTU").get_active_text()
			clusteridentity = str(self.builder.get_object("spnQCluster").get_value())
			otuflags = self.builder.get_object("txtQOTUFlags").get_text()
			oturefseqs = self.builder.get_object("txtQOTURefSeqs").get_text()
			otublastdb = self.builder.get_object("txtQOTUBlastDB").get_text()
			verbose = str(self.builder.get_object("chkQVerbose").get_active())
			items = [alignmethod, phylomethod, otumethod, clusteridentity, \
			otuflags, oturefseqs, otublastdb, taxmethod, verbose]
			labels = ["align-method", "phylogeny-method", "otu-method", \
			"cluster-identity", "otu-flags", "otu-refseqs", "otu-blastdb", \
			"classification-method", "verbose"]

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
		self.XMLOutput = "<?xml version=\"1.0\"?>\n<!-- Generated by AXIOMETIC v 0.2 -->\n"
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
				+ row[2] + "\" version=\"" + row[6] + "\""
				if (row[3] != None) & (row[3] != ""):
					self.XMLOutput += " fprimer=\"" + row[3] + "\""
				if (row[4] != None) & (row[4] != ""):
					self.XMLOutput += " rprimer=\"" + row[4] + "\""
				if (row[5] != None) & (row[5] != ""):
					self.XMLOutput += " threshold=\"" + row[5] + "\""
				self.XMLOutput += ">\n"
				searchterm = "tag"
			for sample in self.SampleData[i]:
				self.XMLOutput += "\t\t<sample " + searchterm + "=\"" + sample["regextag"] + "\""
				j = 1
				for label in self.MetadataLabels:
					try:
						self.XMLOutput += " " + label + "=\"" + sample[label] + "\""
					except:
						pass
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
			
	### Window Setup Functions ###
	def setup_metadata_window(self):
		self.builder.add_from_file(determine_path() + "/res/DefineMetadata.ui")
		self.builder.connect_signals(self)
		DefineMetadata = self.builder.get_object("axiome_define_metadata")
		return DefineMetadata
		
	def setup_sourcefiles_window(self):
		self.builder.add_from_file(determine_path() + "/res/DefineSourceFiles.ui")
		self.builder.connect_signals(self)
		DefineSourceFiles = self.builder.get_object("axiome_define_source_files")
		return DefineSourceFiles
		
	def setup_samplefiles_window(self):
		self.builder.add_from_file(determine_path() + "/res/DefineSamples.ui")
		self.builder.connect_signals(self)
		DefineSamples = self.builder.get_object("axiome_define_samples")
		return DefineSamples
		
	def setup_analyses_window(self):
		self.builder.add_from_file(determine_path() + "/res/DefineAnalyses.ui")
		self.builder.connect_signals(self)
		DefineAnalyses = self.builder.get_object("axiome_define_analyses")
		#Set up the QIIME analysis as default
		cmbPipeline = self.builder.get_object("cmbPipeline")
		cmbQOTU = self.builder.get_object("cmbQOTU")
		cmbQAlign = self.builder.get_object("cmbQAlign")
		cmbQPhylo = self.builder.get_object("cmbQPhylo")
		cmbMOTU = self.builder.get_object("cmbMOTU")
		cmbQTax = self.builder.get_object("cmbQTaxMethod")
		cmbQOTU.set_active(7)
		cmbQAlign.set_active(2)
		cmbQPhylo.set_active(0)
		cmbQTax.set_active(0)
		cmbMOTU.set_active(0)
		cmbPipeline.get_model().clear()
		for key in self.pluginDefs.pipe_analysis_dict:
			cmbPipeline.append_text(key)
		cmbPipeline.set_active(0)
		return DefineAnalyses
		
	def __init__(self):
	    self.builder = gtk.Builder()
	    self.builder.add_from_file(determine_path() + "/res/AxiomeUiWindow.ui")
	    self.builder.connect_signals(self)
	    self.IntroWindow = self.builder.get_object("axiome_ui_window")
	    self.pluginDefs = analysisDefs(determine_path() + "/res/plugin-defs.xml")
	    
	    self.DefineMetadata = self.setup_metadata_window()
	    self.MetadataLabels = None
	    
	    self.DefineSourceFiles = self.setup_sourcefiles_window()
	    
	    self.DefineSamples = self.setup_samplefiles_window()
	    self.SampleData = list()
	    self.DefineAnalyses = self.setup_analyses_window()
	    
	    
	    #Misc things to keep track of things without having to jump
	    # through GTK parent/child lookup hoops
	    self.Editing = None
	    self.PropContainer = None
	    self.ConstructedAnalysisInfo = None
	    self.SampleFileIndex = 0
	    self.XMLOutput = None
	    self.OpenAX = None
	    self.IntroWindow.show()
	    
def main():
	mainWindow = WindowManager()
	gtk.main()

if __name__ == '__main__':
	main()
