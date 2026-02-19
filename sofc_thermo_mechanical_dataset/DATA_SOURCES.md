# SOFC Data Sources Guide

This document provides references to legitimate data sources for Solid Oxide Fuel Cell (SOFC) research, particularly for thermo-mechanical behavior studies.

## ⚠️ Important Note

The CSV files in this package contain **SYNTHETIC/ILLUSTRATIVE DATA** generated based on published literature ranges. This guide points to sources where you can find **REAL experimental data** for your research.

---

## 1. Open-Access SOFC Datasets

### SOFC-Exp Corpus
- **Description**: Text-mining resources for SOFC experimental data extracted from 45 research papers
- **URL**: https://github.com/boschresearch/sofc-exp_textmining_resources
- **Content**: Structured experimental data on SOFC performance, materials, and operating conditions
- **Format**: JSON, CSV
- **Citation**: Provided in repository

### Hugging Face - SOFC Materials Articles
- **Description**: Dataset of SOFC materials research articles
- **URL**: https://huggingface.co/datasets/boschresearch/sofc_materials_articles
- **Content**: Text corpus of scientific articles on SOFC materials
- **Use**: Natural language processing and data extraction

---

## 2. Material Property Datasheets

### Crofer 22 APU (Interconnect Material)

#### Official VDM Metals Datasheet
- **URL**: https://www.vdm-metals.com/fileadmin/user_upload/Downloads/Data_Sheets/Data_Sheet_VDM_Crofer_22_APU.pdf
- **Content**: 
  - Chemical composition
  - Thermal expansion coefficient (CTE)
  - Thermal conductivity
  - Mechanical properties (tensile strength, yield strength)
  - Oxidation resistance data
  - Temperature range: RT to 900°C

#### UL Prospector - Crofer 22 APU
- **URL**: https://www.ulprospector.com/metals/en/datasheet/223565/crofer-22-apu
- **Content**: Comprehensive material properties database entry

### YSZ (Yttria-Stabilized Zirconia)

#### MatWeb Database
- **URL**: http://www.matweb.com/search/DataSheet.aspx?MatGUID=43c6d0b8d13f405c9f1ce9f6af0ec5d1
- **Content**: Comprehensive material properties for 8YSZ (8 mol% Y₂O₃)

### LSM, LSCF, and Other Cathode Materials
- Refer to manufacturer datasheets from:
  - Fuel Cell Materials (https://fuelcellmaterials.com/)
  - MSE Supplies (https://www.msesupplies.com/)
  - Ceraco (https://www.ceraco.de/)

---

## 3. Key Research Papers with Experimental Data

### Recent High-Impact Studies

#### 1. Long-term Thermo-Mechanical Performance
**Reference**: Guo et al. (2024)  
**Title**: "Long-term thermo-mechanical performance evolution of SOFC stacks"  
**DOI**: Contact journal or search databases  
**Data**: Thermal cycling tests, degradation rates, crack propagation

#### 2. 3D Microstructure Reconstruction
**Reference**: Xiang et al. (2020)  
**Title**: "3D microstructure reconstruction of SOFC electrodes and quantitative analysis"  
**DOI**: 10.1016/j.jpowsour.2020.227824 (example format)  
**Data**: Porosity, tortuosity, grain size measurements

#### 3. Synchrotron XRD Study
**Reference**: Heenan et al. (2018)  
**Title**: "An advanced microstructural and electrochemical datapoint for SOFC electrode"  
**Journal**: Scientific Data  
**Data**: High-resolution microstructural data

#### 4. Thermo-Mechanical Reliability During Cycling
**Reference**: Greco et al. (2015)  
**Title**: "Thermo-mechanical reliability of ceramic materials for SOFC applications"  
**Data**: Thermal cycling stability, stress measurements

#### 5. Thermal Cycling Tests
**Reference**: Noh et al. (2014)  
**Title**: "Thermal cycling stability of NiO/YSZ anode-supported SOFC"  
**Data**: Multiple thermal cycle protocols, degradation analysis

### Open Access Articles

#### MDPI - Thermal Cycling Stability
**Title**: "Thermal Cycling Stability of NiO/YSZ Anode-Supported SOFC Button Cells"  
**URL**: https://www.mdpi.com/2227-9717/13/11/3747  
**Publisher**: MDPI Processes (2024)  
**Content**: 
- Experimental thermal cycling protocols
- OCV, ASR, and power density measurements
- SEM and microstructural analysis
- Open access full text

#### IntechOpen - Thermomechanics Chapter
**Title**: "Thermomechanics of Solid Oxide Fuel Cell Electrode Microstructures"  
**URL**: https://www.intechopen.com/chapters/60414  
**Content**:
- Theoretical framework
- Computational models
- Stress-strain relationships
- Free to read online

---

## 4. General Materials Databases

### NIST Materials Data Repository
- **URL**: https://materialsdata.nist.gov/
- **Content**: Validated materials data including high-temperature ceramics
- **Search**: "zirconia", "SOFC", "ceramic"

### Materials Project
- **URL**: https://materialsproject.org/
- **Content**: Computational materials database
- **Data**: Crystal structures, thermodynamic properties, elastic constants
- **API**: Available for programmatic access

### Citrination / Citrine Informatics
- **URL**: https://citrination.com/ (now part of Citrine Platform)
- **Content**: AI-driven materials database
- **Access**: Registration required; some public datasets available

### MatWeb
- **URL**: http://www.matweb.com/
- **Content**: Largest database of material properties
- **Search**: By material name, property, manufacturer
- **Categories**: Metals, ceramics, polymers

### Granta EduPack / Ansys GRANTA
- **URL**: https://www.ansys.com/products/materials/granta-edupack
- **Content**: Educational materials database
- **Access**: Free for academic institutions
- **Features**: Material selection tools, property charts

---

## 5. Government & National Laboratory Sources

### DOE/NETL SOFC Program
- **Organization**: U.S. Department of Energy, National Energy Technology Laboratory
- **URL**: https://netl.doe.gov/ (search for "SOFC")
- **Content**: 
  - Technical reports
  - Research findings
  - Performance benchmarks
  - Some datasets available through OSTI.gov

### Forschungszentrum Jülich (FZJ)
- **Country**: Germany
- **URL**: https://www.fz-juelich.de/en/iek/iek-1
- **Research**: Leading European SOFC research center
- **Publications**: Extensive publication list with experimental data
- **Contact**: Many datasets available upon request

### German Aerospace Center (DLR)
- **Institute**: Institute of Engineering Thermodynamics
- **URL**: https://www.dlr.de/tt/en/
- **Research**: SOFC stack development and testing
- **Data**: Stack characterization, long-term testing results

### Pacific Northwest National Laboratory (PNNL)
- **URL**: https://www.pnnl.gov/
- **Research**: SOFC materials and durability
- **Data Portal**: Some datasets on data.gov

---

## 6. Scientific Data Repositories

### Zenodo
- **URL**: https://zenodo.org/
- **Search**: "SOFC", "solid oxide fuel cell", "YSZ", "thermal cycling"
- **Content**: Datasets associated with publications, often with DOI
- **License**: Varies by dataset (many CC-BY)

### Figshare
- **URL**: https://figshare.com/
- **Search**: Similar to Zenodo
- **Content**: Research outputs including datasets, figures, presentations
- **Features**: Easy data visualization and download

### NREL Data Catalog
- **Organization**: National Renewable Energy Laboratory
- **URL**: https://data.nrel.gov/
- **Content**: Energy-related datasets including fuel cells
- **API**: Available for programmatic access

### Dryad Digital Repository
- **URL**: https://datadryad.org/
- **Content**: Datasets underlying scientific publications
- **Search**: Author, keyword, DOI

### Mendeley Data
- **URL**: https://data.mendeley.com/
- **Content**: Research data repository
- **Integration**: Linked with Mendeley reference manager

---

## 7. How to Request Data from Authors

Many high-quality datasets are not publicly available but can be obtained by contacting the authors:

### Best Practices for Data Requests

1. **Find Recent Papers**: Search Google Scholar, Web of Science, or Scopus for recent SOFC papers
   - Keywords: "SOFC thermal cycling", "SOFC mechanical properties", "SOFC degradation"

2. **Email Template**:
   ```
   Subject: Data Request for [Paper Title]
   
   Dear Dr. [Author Name],
   
   I am a [researcher/student] at [Institution] working on [brief description].
   I recently read your paper "[Paper Title]" published in [Journal, Year].
   
   I am particularly interested in [specific data/measurements] presented in 
   Figure/Table X. Would it be possible to share the underlying data for my 
   research? I will properly cite your work in any publications resulting from 
   this research.
   
   Thank you for considering my request.
   
   Best regards,
   [Your Name]
   [Affiliation]
   [Email]
   ```

3. **What to Ask For**:
   - Raw data tables (CSV, Excel)
   - Measurement conditions and protocols
   - Statistical information (error bars, number of samples)
   - Instrument specifications

4. **Offer Collaboration**: Sometimes authors prefer collaboration to simple data sharing

---

## 8. Material Property Estimation

### When Experimental Data is Unavailable

#### Empirical Correlations
- Use established relationships (e.g., CTE vs temperature for ceramics)
- Reference handbooks: ASM Materials Handbook, Ceramics Handbook

#### Rule of Mixtures
- For composite materials (e.g., Ni-YSZ): Properties can be estimated from constituents
- Example: E_composite ≈ V_Ni × E_Ni + V_YSZ × E_YSZ

#### Computational Tools
- **DFT Calculations**: For crystal structures and elastic constants
- **Molecular Dynamics**: For thermal properties
- **Phase Diagrams**: For stability regions

#### Property Databases for Components
- **Ni (Nickel)**: Well-documented metal properties
- **YSZ**: Extensive ceramic database entries
- **Perovskites** (LSM, LSCF): Literature surveys available

---

## 9. Proper Citation Practices

### For Datasets

When using external datasets:

```
[Author(s)]. (Year). Dataset Title [Data set]. Repository Name. 
DOI or URL
```

Example:
```
Smith, J., et al. (2023). SOFC Thermal Cycling Experimental Data [Data set]. 
Zenodo. https://doi.org/10.5281/zenodo.1234567
```

### For This Synthetic Dataset

When using this educational package:

```
This analysis uses synthetic/illustrative data from the SOFC 
Thermo-Mechanical Dataset Package (educational resource, 2024). 
The data values are based on published literature ranges but are 
NOT real experimental measurements.
```

Always clearly state when using synthetic vs. experimental data.

---

## 10. Additional Resources

### Review Papers
- Search for "SOFC review" in major journals
- Topics: Materials selection, degradation mechanisms, thermal management
- These often compile data from multiple sources

### Handbooks
- **SOFC Handbook** - Various editions available
- **Fuel Cell Handbook** (DOE publication) - Free PDF available
- **High-Temperature Solid Oxide Fuel Cells** (Singhal & Kendall)

### Conferences
- **ECS (Electrochemical Society)** - SOFC section
- **European SOFC Forum**
- **Fuel Cell Seminar & Energy Exposition**
- Proceedings often contain experimental data

### Standards
- **ASTM Standards**: Mechanical testing of ceramics
- **IEC Standards**: Fuel cell testing protocols
- **JRC (Joint Research Centre)**: European SOFC testing procedures

---

## 11. Data Quality Assessment

### When Evaluating Data Sources

Check for:
- ✅ **Measurement methodology** clearly described
- ✅ **Sample preparation** and composition specified
- ✅ **Operating conditions** (temperature, atmosphere, etc.)
- ✅ **Error bars or uncertainty** provided
- ✅ **Reproducibility** (multiple samples/tests)
- ✅ **Peer review** status
- ✅ **Author credentials** and institution

### Red Flags
- ❌ No experimental details
- ❌ Values far outside typical ranges
- ❌ No uncertainty estimates
- ❌ Contradicts multiple reliable sources
- ❌ No author contact information

---

## 12. Contributing to This Guide

If you know of additional high-quality SOFC data sources, please contribute:

1. Open an issue or pull request on the GitHub repository
2. Include: URL, description, data types available, access requirements
3. Verify the source is legitimate and maintained

---

## Summary

This guide provides pathways to legitimate SOFC experimental data. Remember:

- **Always verify data** against multiple sources when possible
- **Document your sources** meticulously in your research
- **Respect copyright** and licensing terms
- **Contact authors** when data is not openly available
- **Contribute back** to the community when you can

For questions or suggestions about this guide, please open an issue on the GitHub repository.

---

*Last Updated: 2024*  
*This is a living document - contributions welcome!*
