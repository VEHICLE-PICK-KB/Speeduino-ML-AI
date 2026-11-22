# Speeduino ML — Source register

Updated: 16 November 2026

Working source register for the Applied Machine Learning project. Add sources as they are consulted, with the claims or implementation decisions they support. This is not yet the final report bibliography. Stable IDs below are working identifiers; final IEEE citation numbers must follow first appearance in the report.

## Technical sources

### SRC-001 — MLG binary file format

- **Author:** Philip Tobin.
- **Organisation:** EFI Analytics.
- **Title:** Binary MLG Logging (MLVLG) file format specification.
- **Version:** Format version 2; document revision 0.94, 8 August 2022.
- **Type:** Primary technical specification, not a peer-reviewed research paper.
- **URL:** https://www.efianalytics.com/TunerStudio/docs/MLG_Binary_LogFormat_2.0.pdf
- **Accessed:** 16 November 2026.
- **Status:** Consulted; used to verify the converter V2 changes.

**Use in the project:** Explain the MLG-to-CSV conversion in Methodology: header parsing, field definitions, big-endian byte order, value scaling, measurement blocks, marker blocks and checksum validation.

**Relevant sections and details:**

- Header; Logger Field — scalar: field names, units, types and scaling. DisplayValue = (rawValue + transform) × scale.
- Section 2.2.1.1, Type: Logger Field Data: type 0 measurement block; four prefix bytes, field payload and one checksum byte. Checksum is the sum of payload bytes modulo 256.
- Section 2.2.1.2, Type: Marker: type 1 marker; four prefix bytes and a 50-byte comment, totalling 54 bytes.
- For logs, the measurement payload is 91 bytes, so a complete measurement block occupies 96 bytes. This size comes from our file headers; it is not a universal MLG record size.

**Implementation evidence:** The original converter advanced past markers as if they were measurement blocks. V2 handles the two block sizes separately. All 17 supplied logs passed V2 payload checksum checks; logs without markers produced unchanged DataFrames compared with V1. The user also confirmed that V2 resolved the observed CSV issue. This evidence validates the conversion checks performed, not the physical accuracy of the sensors.

**Limitations:** This source documents the file format. It does not establish engine risk thresholds, prove the cause of an ECU reset, or validate detonation-risk labels.

**Draft IEEE entry (number assigned later):**

P. Tobin, “Binary MLG Logging (MLVLG) file format specification,” EFI Analytics, format ver. 2, rev. 0.94, Aug. 8, 2022. Accessed: Nov. 16, 2026. [Online]. Available: https://www.efianalytics.com/TunerStudio/docs/MLG_Binary_LogFormat_2.0.pdf

### SRC-002: Pandas documentation

- URL: https://pandas.pydata.org/docs/
- Accessed: 22 November 2026.
- Use: CSV reading, DataFrames, missing values, indexing,
  summary calculations and time series plots.
- Plotting reference:
  https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.plot.html

### SRC-003: Matplotlib documentation

- URL: https://matplotlib.org/stable/
- Accessed: 22 November 2026.
- Use: Displaying, formatting and saving figures.
- Pyplot reference:
  https://matplotlib.org/stable/api/pyplot_summary.html

## Writing and assignment guidance

### GUIDE-001 — University writing guidelines

- **Organisation:** University of Vaasa.
- **Title:** Writing Guidelines.
- **URL:** https://www.uwasa.fi/en/students/writing-guidelines-and-plagiarism-detection/writing-guidelines
- **Accessed:** 16 November 2026.
- **Status:** Consulted for report presentation and source use.
- **Use:** Report layout, figures and captions, references, accessibility and disclosure of AI use.
- **Course-specific requirement:** The supplied assignment slides require IEEE citation style, English, an IMRaD structure and a maximum of 30 pages. Our working target is approximately 15 pages overall. Apply the course-specific IEEE requirement when preparing citations.
- **Classification:** Writing guidance; not research evidence for the technical hypotheses. Include in the final bibliography only if cited in the report.

## Research sources still to be added

No research literature entries have been added yet. The user has additional sources to review later. Record their verified bibliographic details and the exact claims they support before citing them.

Topics requiring research support:

- Relationships between available engine signals and potentially detonation-prone conditions.
- Assumptions and limitations of simulated fuel-delivery and ignition-timing disturbances.
- Selected ML methods and their mathematical principles.
- Time-series features, evaluation design and prevention of data leakage.

## Template for a new source

### SRC-XXX — Short descriptive title

- **Authors / organisation:**
- **Title:**
- **Year / version:**
- **Publication / DOI / URL:**
- **Accessed (for online sources):**
- **Type:** Research paper / technical specification / official documentation / other.
- **Status:** Candidate / read / used.
- **Claims or decisions supported:**
- **Relevant sections, pages or figures:**
- **Limitations:**
- **Draft IEEE entry:**
