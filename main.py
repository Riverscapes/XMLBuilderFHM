import os
from os.path import join
from XMLBuilder import XMLBuilder
import re
import time
import datetime
import uuid


def generate_project_xml(project_root):
    """
    Creates a project.rs.xml file at the given path
    :param project_root: The path to where we want to make an xml file
    :return:
    """
    xml_file = project_root + "\project.rs.xml"
    if os.path.exists(xml_file):
        os.remove(xml_file)

    watershed = os.path.basename(os.path.dirname(project_root))
    if watershed == "JohnDay":
        watershed = "John Day"
    site = os.path.basename(project_root)

    new_xml_file = XMLBuilder(xml_file,
                              "Project",
                              [('xmlns:xsi', "http://www.w3.org/2001/XMLSchema-instance"),
                               ('xsi:noNamespaceSchemaLocation', "https://raw.githubusercontent.com/Riverscapes/Program/master/Project/XSD/V1/Project.xsd")])

    new_xml_file.add_sub_element(new_xml_file.root, "Name", site)
    new_xml_file.add_sub_element(new_xml_file.root, "ProjectType", "FHM")

    has_metadata = False
    has_realization = False

    for year_file in os.listdir(project_root):
        match = re.match(r'201[2|3|4|5|6]', year_file)
        if match:
            year_path = join(project_root, year_file)
            year = year_file

        for file in os.listdir(year_path):
            match = re.match(r'VISIT_([\d]+)', file)
            if match:
                data = match.groups()
                visit_id = data[0]
                visit_path = join(year_path, file)

        for file in os.listdir(visit_path):
            match = re.match(r'S[\d_]+', file)
            if match:
                flow_path = join(visit_path, file)
                flow = file

        root_to_flow_path = year + '\VISIT_' + visit_id + '\\' + flow

        if not has_metadata:
            add_meta_data(new_xml_file, flow_path, watershed, site)
            has_metadata = True

        if not has_realization:
            realizations_element = new_xml_file.add_sub_element(new_xml_file.root, "Realizations")
            has_realization = True

        add_fhm(new_xml_file, realizations_element, flow_path, root_to_flow_path, year, visit_id, flow)

    new_xml_file.write()


def add_meta_data(new_xml_file, flow_path, watershed, site):
    meta_data_element = new_xml_file.add_sub_element(new_xml_file.root, "MetaData")

    temp_path = flow_path + "\Analyses\FIS\Chinook\Spawner\Run_01\FuzzyHQ.tif"
    year, month, day, hour, min, sec, wday, yday, isdst = time.gmtime(os.path.getmtime(temp_path))
    creation_time = datetime.datetime(year, month, day, hour, min, sec)

    new_xml_file.add_sub_element(meta_data_element, "Meta", creation_time.isoformat(),
                                 [("name", "CreatedOn")])
    new_xml_file.add_sub_element(meta_data_element, "Meta", "CRB", [("name", "Region")])
    new_xml_file.add_sub_element(meta_data_element, "Meta", site, [("name", "Site")])
    new_xml_file.add_sub_element(meta_data_element, "Meta", watershed, [("name", "Watershed")])


def add_inputs(new_xml_file, realizations_element, flow_path, root_to_flow_path, year, visit_id, flow):
    inputs_path = join(flow_path, "Inputs")
    root_to_inputs_path = root_to_flow_path + '\Inputs'
    if not os.path.exists(inputs_path):
        return
    input_element = new_xml_file.add_sub_element(realizations_element, "Inputs")

    if os.path.exists(inputs_path + "\CoverIndex\CoverIndex.tif"):
        cover_element = new_xml_file.add_sub_element(input_element, "Cover",
                                                     tags=[("id", year + "_VISIT_" + visit_id + '_' + flow + '_CoverIndex')])
        new_xml_file.add_sub_element(cover_element, "Name", year + ' Visit ' + visit_id + ' ' + flow + " Cover Index")
        new_xml_file.add_sub_element(cover_element, "Path", root_to_inputs_path + "\CoverIndex\CoverIndex.tif")

    if os.path.exists(inputs_path + "\GrainSize\D50.tif"):
        substrate_element = new_xml_file.add_sub_element(input_element, "Substrate",
                                                         tags=[('id', year + "_VISIT_" + visit_id + '_' + flow + '_Substrate')])
        new_xml_file.add_sub_element(substrate_element, "Name", year + ' Visit ' + visit_id + ' ' + flow + " Substrate")
        new_xml_file.add_sub_element(substrate_element, "Path", root_to_inputs_path + "\GrainSize\D50.tif")

    if os.path.exists(inputs_path + "\Hydraulics\Vel.tif"):
        velocity_element = new_xml_file.add_sub_element(input_element, "Velocity",
                                                        tags=[("id", year + "_VISIT_" + visit_id + '_' + flow + '_Velocity')])
        new_xml_file.add_sub_element(velocity_element, "Name", year + ' Visit ' + visit_id + ' ' + flow + " Velocity")
        new_xml_file.add_sub_element(velocity_element, "Path", root_to_inputs_path + "\Hydraulics\Vel.tif")


    if os.path.exists(inputs_path + "\Hydraulics\Depth.tif"):
        depth_element = new_xml_file.add_sub_element(input_element, "Depth",
                                                     tags=[('id', year + "_VISIT_" + visit_id + '_' + flow + '_Depth')])
        new_xml_file.add_sub_element(depth_element, "Name", year + ' Visit ' + visit_id + ' ' + flow + " Depth")
        new_xml_file.add_sub_element(depth_element, "Path", root_to_inputs_path + "\Hydraulics\Depth.tif")


def add_fhm(new_xml_file, realizations_element, flow_path, root_to_flow_path, year, visit_id, flow):
    temp_path = flow_path + "\Analyses\FIS\Chinook\Spawner\Run_01\FuzzyHQ.tif"
    creation_year, month, day, hour, min, sec, wday, yday, isdst = time.gmtime(os.path.getmtime(temp_path))
    creation_time = datetime.datetime(creation_year, month, day, hour, min, sec)

    fhm_element = new_xml_file.add_sub_element(realizations_element, "FHM", tags=[('id', flow),
                                                                                  ("dateCreated", creation_time.isoformat()),
                                                                                  ("productVersion", '0.0.1'),
                                                                                  ("guid", getUUID())])
    new_xml_file.add_sub_element(fhm_element, "Name")
    meta_data_element = new_xml_file.add_sub_element(fhm_element, "MetaData")
    new_xml_file.add_sub_element(meta_data_element, "Meta", visit_id, tags=[("name", "Visit")])
    new_xml_file.add_sub_element(meta_data_element, "Meta", flow, tags=[('name', "Discharge")])

    add_inputs(new_xml_file, fhm_element, flow_path, root_to_flow_path, year, visit_id, flow)

    analyses_element = new_xml_file.add_sub_element(fhm_element, "Analyses")
    add_analysis(new_xml_file, analyses_element, flow_path, root_to_flow_path, year, visit_id, flow, "Chinook", "Spawner")
    add_analysis(new_xml_file, analyses_element, flow_path, root_to_flow_path, year, visit_id, flow, "Steelhead", "Spawner")
    add_analysis(new_xml_file, analyses_element, flow_path, root_to_flow_path, year, visit_id, flow, "Chinook", "Juvenile")
    add_analysis(new_xml_file, analyses_element, flow_path, root_to_flow_path, year, visit_id, flow, "Steelhead", "Juvenile")


def add_analysis(new_xml_file, analyses_element, flow_path, root_to_flow_path, year, visit_id, flow, fish, lifestage):
    analysis_path = flow_path + "\\Analyses"
    root_to_analyses_path = root_to_flow_path + "\\Analyses"
    if os.path.exists(analysis_path + "\FIS\\" + fish + "\\" + lifestage + "\Run_01\FuzzyHQ.tif") or os.path.exists(analysis_path + "\HSI\\" + fish + "\\" + lifestage + "\Run_01\HSI.tif"):
        analysis_element = new_xml_file.add_sub_element(analyses_element, "Analysis")

        new_xml_file.add_sub_element(analysis_element, "Name", year + " Visit " + visit_id + " " +
                                     flow + " " + fish + " " + lifestage)

        # begins models subtree
        models_element = new_xml_file.add_sub_element(analysis_element, "Models")
    # begins FIS subtree
    if os.path.exists(analysis_path + "\FIS\\" + fish + "\\" + lifestage + "\Run_01\FuzzyHQ.tif"):
        fis_element = new_xml_file.add_sub_element(models_element, "FIS")
        if lifestage == "Spawner":
            new_xml_file.add_sub_element(fis_element, "FISFile", root_to_analyses_path + "\FIS\\" + fish +
                                         "\Spawner\Run_01\FISModel\Fuzzy" + fish + "Spawner_DVSC.fis")

        meta_data_element = new_xml_file.add_sub_element(fis_element, "MetaData")
        new_xml_file.add_sub_element(meta_data_element, "Meta", fish, [('name', 'Species')])
        new_xml_file.add_sub_element(meta_data_element, "Meta", lifestage, [('name', 'LifeStage')])

        # begins output subtree
        outputs_element = new_xml_file.add_sub_element(fis_element, "Outputs")

        # begins raster subtree
        raster_element = new_xml_file.add_sub_element(outputs_element, "Raster", tags=[('id', "raster_01")])
        new_xml_file.add_sub_element(raster_element, "Name", "Fish Habitat")
        new_xml_file.add_sub_element(raster_element, "Path", root_to_analyses_path + "\FIS\\" + fish + "\\" + lifestage + "\Run_01\FuzzyHQ.tif")

        meta_data_element = new_xml_file.add_sub_element(raster_element, "MetaData")
        new_xml_file.add_sub_element(meta_data_element, "Meta", tags=[('name', 'Type')])
        # ends raster subtree

        metrics_element = new_xml_file.add_sub_element(fis_element, "Metrics")
        new_xml_file.add_sub_element(metrics_element, "Metric", "0.0", [('name', "WUA")])
        # ends FIS subtree

    # begins HSI subtree
    if os.path.exists(analysis_path + "\HSI\\" + fish + "\\" + lifestage + "\Run_01\HSI.tif"):
        hsi_element = new_xml_file.add_sub_element(models_element, "HSI")

        meta_data_element = new_xml_file.add_sub_element(hsi_element, "MetaData")
        new_xml_file.add_sub_element(meta_data_element, "Meta", fish, [('name', "Species")])
        new_xml_file.add_sub_element(meta_data_element, "Meta", lifestage, [('name', 'LifeStage')])

        # begins outputs tree
        outputs_element = new_xml_file.add_sub_element(hsi_element, "Outputs")

        # begins raster subtree
        raster_element = new_xml_file.add_sub_element(outputs_element, "Raster", tags=[('id', "raster_02")])
        new_xml_file.add_sub_element(raster_element, "Name", "Fish Habitat")
        new_xml_file.add_sub_element(raster_element, "Path", root_to_analyses_path + "\HSI\\" + fish + '\\' +
                                     lifestage + "\Run_01\HSI.tif")

        meta_data_element = new_xml_file.add_sub_element(raster_element, "MetaData")
        new_xml_file.add_sub_element(meta_data_element, "Meta", tags=[('name', "Type")])
        # ends raster subtree

        metrics_element = new_xml_file.add_sub_element(hsi_element, "Metrics")
        new_xml_file.add_sub_element(metrics_element, "Metric", "0.0", [("name", "WUA")])


def main(FHM_data_root):
    print "Creating XML project files..."
    for root, dirs, files in os.walk(FHM_data_root):
        if '2012' in dirs or '2013' in dirs or '2014' in dirs or '2015' in dirs or '2016' in dirs:
            generate_project_xml(root)

    print "XML project files created"


def getUUID():
    return str(uuid.uuid4()).upper()


if __name__ == '__main__':
    main("C:\Users\A02150284\Documents\NewFHMData")
