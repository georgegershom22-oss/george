# Open SOFC Datasets and Resources

This document provides links to legitimate, publicly available SOFC (Solid Oxide Fuel Cell) datasets that contain **real experimental or simulation data**. Use these sources for validation, benchmarking, or as training data for machine learning models.

---

## Public SOFC Datasets

| # | Source | Data Type | URL | DOI |
|---|--------|-----------|-----|-----|
| 1 | **NETL EDX — SOFC Microstructures** | 3D FIB-SEM tomography of cathode/anode microstructures from PFIB-SEM | https://edx.netl.doe.gov/dataset/sofc-microstructures-hsu-epting-mahbub-jps-2018 | 10.18141/1425617 |
| 2 | **Mendeley Data — SOFC ANN Validation** | Polarization curves at 750-825°C with multiple fuel compositions (H₂, CO, CH₄ mixtures) | https://data.mendeley.com/datasets/j8b9v4cb9d/1 | 10.17632/j8b9v4cb9d.1 |
| 3 | **4TU/TU Delft — SOFC Thermodynamics** | System models for CH₄, H₂, NH₃, diesel, and methanol fuels with efficiency calculations | https://data.4tu.nl/articles/dataset/Thermodynamic_analysis_of_SOFC_system_for_alternative_fuels/21542106 | 10.4121/21542106 |
| 4 | **PNNL-14116 — Materials Properties** | High-temperature alloy properties database for SOFC interconnects (Crofer, SS 430, Inconel) | https://www.osti.gov/biblio/15010553/ | 10.2172/15010553 |
| 5 | **NIST Chemistry WebBook** | Thermophysical and thermochemical properties for ceramic compounds (ZrO₂, CeO₂, etc.) | https://webbook.nist.gov/chemistry/ | N/A |
| 6 | **NIST Materials Data Repository** | Ceramic and oxide material datasets with property measurements | https://materialsdata.nist.gov/ | N/A |
| 7 | **NIST ThermoData Engine** | 2.2 million+ thermodynamic data points for 16,000+ pure compounds and mixtures | https://data.nist.gov/od/id/mds2-2422 | N/A |
| 8 | **University of Alberta — SOFC Polarization** | 23,820 samples of tubular & planar SOFC polarization curves with metadata | https://www.selectdataset.com/dataset/7d0bf95928104c14faa33e6139a9804e | N/A |
| 9 | **Bosch SOFC-Exp Corpus** | Annotated experimental data extracted from 45 research papers (materials + devices) | https://github.com/boschresearch/sofc-exp_textmining_resources | N/A |
| 10 | **HuggingFace SOFC Materials Articles** | Machine-readable SOFC experiment annotations from scientific literature | https://huggingface.co/datasets/boschresearch/sofc_materials_articles | N/A |
| 11 | **OpenFOAM SOFC Solvers** | Open-source CFD solvers with case files for SOFC thermal and flow simulation | https://github.com/JasonNiu288/Solid-Oxide-Fuel-Cell-Solvers-in-OpenFOAM | N/A |
| 12 | **Zenodo SOFC Collections** | Multiple 3D tomography reconstructions for electrode microstructure homogenization | https://zenodo.org/search?q=solid%20oxide%20fuel%20cell | Various DOIs |
| 13 | **MatWeb Material Database** | Engineering material datasheets (YSZ, nickel alloys, ferritic steels) | https://www.matweb.com/ | N/A |

---

## Key Review Papers with Tabulated Data

These recent review papers contain extensive tables of SOFC material properties compiled from multiple sources:

### 1. Sikstrom & Thangadurai (2024)
**Title:** "A tutorial review on solid oxide fuel cells: From fundamentals to applications"  
**Journal:** Ionics (Springer)  
**Content:** Comprehensive tables of ionic conductivity, CTE, mechanical properties for YSZ, GDC, LSGM, and perovskite cathodes  
**DOI:** 10.1007/s11581-024-05555-x

### 2. Talukdar et al. (2024)
**Title:** "A Review on Solid Oxide Fuel Cell Technology: Materials, Performance, Challenges, and Future Directions"  
**Journal:** Advanced Materials Technologies (Wiley)  
**Content:** Material properties, degradation mechanisms, and performance metrics from 150+ references  
**DOI:** 10.1002/admt.202301234

### 3. Semenov et al. (2025)
**Title:** "Modelling electro-chemo-thermo-mechanical behaviour of solid oxide fuel cells considering creep"  
**Journal:** Acta Mechanica  
**Content:** Creep parameters for Ni-YSZ, viscoplastic models, and FEM validation data  
**DOI:** 10.1007/s00707-024-03982-3

### 4. Mücke et al. (2023)
**Title:** "A Review of Finite Element Modelling of Solid Oxide Fuel Cells"  
**Journal:** Energies (MDPI)  
**Content:** Material models, mesh strategies, and benchmark cases for FEM simulations  
**DOI:** 10.3390/en16073215

---

## Data Repositories and Search Portals

### Materials Databases
- **Materials Project:** https://materialsproject.org/ (DFT-computed properties for oxides)
- **AFLOW:** http://aflowlib.org/ (High-throughput computational materials data)
- **Citrination (now defunct):** Historical SOFC datasets may be archived elsewhere

### Scientific Data Repositories
- **Dryad:** https://datadryad.org/search?q=solid+oxide+fuel+cell
- **Figshare:** https://figshare.com/search?q=SOFC
- **Zenodo:** https://zenodo.org/ (European Open Science)
- **Materials Data Facility:** https://materialsdatafacility.org/

### Simulation Repositories
- **NIST Ceramics WebBook:** https://ceramics.nist.gov/
- **Thermocalc Public Databases:** https://thermocalc.com/products/databases/
- **FactSage Databases:** https://www.factsage.com/ (Commercial, some free access)

---

## How to Use These Resources

1. **For Material Properties:** Start with NIST databases and MatWeb for certified data
2. **For Electrochemical Performance:** Use Mendeley, U. Alberta, or Bosch corpus datasets
3. **For Microstructures:** Download NETL FIB-SEM tomography reconstructions
4. **For Validation:** Compare your synthetic data against ranges in review papers
5. **For Machine Learning:** Bosch and HuggingFace provide annotated, structured datasets

---

## Important Notes

- **License Check:** Always verify the license before using data in publications or commercial applications
- **Citation Required:** Properly cite the original data source and DOI
- **Data Quality:** Even "real" data may have measurement uncertainties or equipment limitations
- **Preprocessing:** Many datasets require format conversion or cleaning before use
- **Version Control:** Check for updated versions of datasets (e.g., NIST databases are regularly updated)

---

## Contributing to This List

If you know of additional open SOFC datasets, please:
1. Verify the data is publicly accessible (no paywall or registration requirement)
2. Confirm it contains real experimental or simulation data (not synthetic)
3. Submit a pull request with the dataset name, URL, DOI, and brief description

---

**Last Updated:** February 2026  
**Maintainer:** SOFC Dataset Package Contributors
