# Feature Specification: Illustrate Chapter 1 (Blueprint Style)

## 1. Goal Description

Revamp the illustrations in Chapter 1 (`01.数据治理核心概念与理论框架`) of the Data Governance documentation. The objective is to replace or add illustrations using the `baoyu-article-illustrator` skill, strictly adhering to the new **Blueprint (蓝图/工程图)** style defined in the project Constitution. This ensures visual consistency with the ongoing updates in Chapters 3-10 and enhances the professional, technical aesthetic of the documentation.

## Clarifications
### Session 2026-02-14
- Q: What is the scope of the "rewrite"? → A: **Illustrations Only** (Keep text, regenerate images).

## 2. User Scenarios

### 2.1 Documentation Reader
- **Scenario**: A reader navigates to Chapter 1 to understand core data governance concepts.
- **Expectation**: They see high-quality, retro-technical "Blueprint" style illustrations that visually explain complex concepts (e.g., Data Governance vs Management, DAMA Wheel, Strategic Value).
- **Benefit**: Improved understanding through consistent, professional visual aids that match the rest of the updated documentation.

### 2.2 Content Maintainer
- **Scenario**: A maintainer updates the documentation or adds new chapters.
- **Expectation**: The illustration style is standardized, making it easy to generate matching visuals for new content using the established configuration.

## 3. Functional Requirements

### 3.1 Unify Illustration Style
- **Requirement**: All illustrations in Chapter 1 must be generated using the **Blueprint** style.
  - **Visuals**: White lines on classic blue background, precise technical details, measurements, grid layout, architectural aesthetics.
  - **Resolution**: 1K (Square 1:1).
  - **Text**: Chinese text labels for key concepts.
- **Scope**:
  - `1.1-data_governance_definition.md`
  - `1.2-dama_dmbok2_framework.md`
  - `1.3-data_governance_principles_methodology.md`

### 3.2 Automation
- **Requirement**: Use the `baoyu-article-illustrator` skill (or a wrapper script similar to `illustrate_chapters_3_10.py`) to automate the prompt generation and image creation process.
- **Behavior**:
  - Analyze markdown content to identify key illustration points.
  - Generate prompts specifically for "Blueprint" style.
  - Call `baoyu-image-gen` to create images.
  - Insert images into the markdown files at appropriate locations.

### 3.3 Content Integrity
- **Requirement**: Ensure existing content (text) is preserved.
- **Requirement**: existing images (if any remain) that do not match the Blueprint style should be replaced or removed.

## 4. Success Criteria

- **Coverage**: All 3 markdown files in Chapter 1 have at least 1-2 Blueprint-style illustrations.
- **Style Compliance**: 100% of new images follow the Blueprint style (Blue background, white lines, technical look).
- **Language**: All text within images is in Chinese.
- **Resolution**: All images are 1K square.
- **Linkage**: All images are correctly referenced in the markdown files and render in a standard markdown viewer.

## 5. Assumptions & Constraints

- **Assumptions**:
  - The `baoyu-article-illustrator` and `baoyu-image-gen` tools are configured and operational.
  - The `illustrate_chapters_3_10.py` script can be adapted or reused for Chapter 1.
  - Doubao API is available for prompt generation.
- **Constraints**:
  - Must strictly follow the `Blueprint` style as per the Constitution v1.2.0.
  - No manual approval required for individual images (batch processing).

## 6. Out of Scope

- Modifying the text content of Chapter 1 (other than image links).
- Illustrating Chapter 2 (unless requested later).
