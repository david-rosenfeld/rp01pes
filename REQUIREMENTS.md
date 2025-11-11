# Software Requirements Specification
## Preliminary Experiments System for LLM Traceability Research

**Document Version:** 1.0  
**Date:** 2025-10-21  
**Standard Compliance:** ISO/IEC/IEEE 29148:2018

---

## 1. INTRODUCTION

### 1.1 Purpose
This document specifies the requirements for a software system designed to execute preliminary experiments for research investigating the impact of requirement traceability data on Large Language Model (LLM) performance in specification-driven coding tasks.

### 1.2 Scope
The Preliminary Experiments System (PES) shall provide a modular, extensible, and data-driven framework for conducting ten categories of preliminary experiments to inform the design of a larger empirical study. The system shall support configuration via external files, execution of experiments with multiple LLM providers, collection and storage of results, and generation of analytical reports.

### 1.3 Intended Audience
This specification is intended for software developers implementing the PES, researchers configuring and executing the experiments, and quality assurance personnel verifying system compliance.

### 1.4 Document Conventions
- The term "shall" indicates a mandatory requirement.
- The term "should" indicates a recommended feature.
- The term "may" indicates an optional feature.
- Requirements are uniquely identified with hierarchical identifiers (e.g., REQ-1.2.3).

### 1.5 References
- ISO/IEC/IEEE 29148:2018 - Systems and software engineering - Life cycle processes - Requirements engineering
- Research Plan: "LLM Traceability Research - Comprehensive To-Do List"
- COMET Dataset Repository: https://gitlab.com/SEMERU-Code-Public/Data/icse20-comet-data-replication-package

---

## 2. OVERALL DESCRIPTION

### 2.1 Product Perspective
The PES is a standalone system that interfaces with:
- External LLM API services (e.g., OpenAI, Anthropic, Google)
- Local file system for dataset access and result storage
- Configuration files in YAML or JSON format

### 2.2 Product Functions
The system shall provide the following major functions:
- Configuration management from external YAML/JSON files
- Execution of ten categories of preliminary experiments
- Integration with multiple LLM providers via abstraction layer
- Data collection and structured storage of experimental results
- Statistical analysis of experimental data
- Report generation in multiple formats (CSV, Markdown, HTML, PDF)

### 2.3 User Classes and Characteristics
**Primary User:** Research scientist conducting LLM experiments
- Technical expertise: High
- Domain knowledge: Software engineering, machine learning, statistics
- Usage frequency: Intermittent during preliminary experiment phase

### 2.4 Operating Environment
- **Platform:** Cross-platform (Linux, macOS, Windows)
- **Python Version:** 3.9 or higher
- **Network:** Internet connectivity required for LLM API access
- **Storage:** Sufficient local storage for datasets (estimated 500 MB) and results

### 2.5 Design and Implementation Constraints
- All configuration data shall be externalized in YAML or JSON format
- Code shall be modular to support independent testing and extension
- API credentials shall be managed via configuration, not hard-coded
- System shall operate with datasets stored locally

### 2.6 Assumptions and Dependencies
- Datasets from COMET replication package are downloaded and available locally
- User has valid API credentials for selected LLM providers
- Python environment has necessary dependencies installed
- User has basic understanding of YAML/JSON configuration syntax

---

## 3. SYSTEM REQUIREMENTS

### 3.1 FUNCTIONAL REQUIREMENTS

#### REQ-3.1 Configuration Management

##### REQ-3.1.1 Configuration File Format Support
The system shall support configuration files in both YAML and JSON formats with functionally equivalent capabilities.

###### REQ-3.1.1.1 YAML Configuration Loading
The system shall parse and load configuration data from YAML files conforming to YAML 1.2 specification.

###### REQ-3.1.1.2 JSON Configuration Loading
The system shall parse and load configuration data from JSON files conforming to JSON specification (RFC 8259).

###### REQ-3.1.1.3 Format Equivalence
For any valid configuration, the system shall produce identical behavior regardless of whether the configuration is provided in YAML or JSON format.

##### REQ-3.1.2 Configuration Validation
The system shall validate all configuration files before experiment execution.

###### REQ-3.1.2.1 Schema Validation
The system shall validate configuration files against a predefined schema that specifies required fields, data types, and valid value ranges.

###### REQ-3.1.2.2 Validation Error Reporting
When validation fails, the system shall report specific errors including field name, expected type or value, and actual value provided.

###### REQ-3.1.2.3 Validation Success Confirmation
When validation succeeds, the system shall log a confirmation message indicating that configuration is valid.

##### REQ-3.1.3 Configuration Hierarchy
The system shall support hierarchical configuration structures with the following top-level sections:

###### REQ-3.1.3.1 Experiment Configuration Section
The system shall load experiment-specific parameters including experiment types to execute, parameters for each experiment type, and execution order.

###### REQ-3.1.3.2 Model Configuration Section
The system shall load model specifications including provider information, model identifiers, API endpoints, authentication credentials (as placeholders or references), and model-specific parameters.

###### REQ-3.1.3.3 Dataset Configuration Section
The system shall load dataset specifications including dataset names, file paths to local dataset directories, and mappings of dataset components (requirements, source code, traceability links).

###### REQ-3.1.3.4 Execution Configuration Section
The system shall load execution control parameters including execution mode (sequential, parallel, selective), resume capability settings, logging verbosity level, and output directory paths.

###### REQ-3.1.3.5 Output Configuration Section
The system shall load output format specifications including enabled output formats (CSV, Markdown, HTML, PDF), report templates, and formatting preferences.

##### REQ-3.1.4 Configuration Override Capability
The system shall support command-line overrides of configuration parameters without modifying configuration files.

###### REQ-3.1.4.1 Command-Line Parameter Syntax
The system shall accept command-line parameters in the format `--section.subsection.parameter=value` to override specific configuration values.

###### REQ-3.1.4.2 Override Precedence
Command-line parameters shall take precedence over values specified in configuration files.

###### REQ-3.1.4.3 Override Validation
The system shall validate command-line overrides using the same validation rules applied to configuration file values.

---

#### REQ-3.2 LLM Integration Layer

##### REQ-3.2.1 LLM Abstraction Layer
The system shall provide an abstraction layer that enables uniform interaction with multiple LLM providers.

###### REQ-3.2.1.1 Provider-Agnostic Interface
The system shall define a common interface for LLM operations including prompt submission, response retrieval, parameter configuration, and error handling.

###### REQ-3.2.1.2 Multiple Provider Support
The system shall support integration with at least the following provider types:
- OpenAI-compatible APIs
- Anthropic Claude APIs
- Google Gemini APIs
- Custom REST APIs with configurable endpoints

###### REQ-3.2.1.3 Backend Pluggability
The system shall allow addition of new LLM provider backends without modifying core experiment logic.

##### REQ-3.2.2 API Communication Backends

###### REQ-3.2.2.1 REST API Backend
The system shall implement a REST API backend that communicates with LLM providers using HTTP/HTTPS requests.

####### REQ-3.2.2.1.1 HTTP Request Construction
The system shall construct HTTP requests with appropriate headers, authentication, request body format, and endpoint URLs based on provider configuration.

####### REQ-3.2.2.1.2 HTTP Response Parsing
The system shall parse HTTP responses from LLM APIs and extract relevant fields including generated text, token usage statistics, error messages, and metadata.

####### REQ-3.2.2.1.3 HTTP Error Handling
The system shall handle HTTP-level errors including network failures (timeout, connection refused), authentication failures (401, 403), rate limiting (429), and server errors (500, 503).

###### REQ-3.2.2.2 SDK Backend
The system shall implement SDK-based backends for providers offering official Python libraries.

####### REQ-3.2.2.2.1 OpenAI SDK Integration
The system shall integrate with the official OpenAI Python library for providers using OpenAI-compatible APIs.

####### REQ-3.2.2.2.2 Anthropic SDK Integration
The system shall integrate with the official Anthropic Python library for Claude models.

####### REQ-3.2.2.2.3 Google SDK Integration
The system shall integrate with the official Google Generative AI Python library for Gemini models.

####### REQ-3.2.2.2.4 SDK Error Handling
The system shall handle SDK-specific exceptions and translate them to a common error representation.

##### REQ-3.2.3 LLM Request Parameters

###### REQ-3.2.3.1 Prompt Configuration
The system shall accept prompt text as a string parameter and support multi-turn conversations where applicable.

###### REQ-3.2.3.2 Temperature Configuration
The system shall support configuration of the temperature parameter with values in the range [0.0, 2.0] and default value configurable per experiment.

###### REQ-3.2.3.3 Max Tokens Configuration
The system shall support configuration of maximum output tokens with values in the range [1, model_maximum] and default value of null (provider determines).

###### REQ-3.2.3.4 Stop Sequence Configuration
The system shall support configuration of stop sequences as a list of strings that terminate generation when encountered.

###### REQ-3.2.3.5 Additional Parameters
The system shall support provider-specific additional parameters through a pass-through mechanism that forwards unrecognized parameters to the provider API.

##### REQ-3.2.4 Response Processing

###### REQ-3.2.4.1 Response Extraction
The system shall extract the generated text from provider responses regardless of provider-specific response format.

###### REQ-3.2.4.2 Metadata Extraction
The system shall extract metadata from responses including token counts (prompt tokens, completion tokens, total tokens), model version/identifier, finish reason, and timestamp.

###### REQ-3.2.4.3 Response Logging
The system shall log all responses with configurable detail level including full prompt and response text at DEBUG level and summary statistics at INFO level.

##### REQ-3.2.5 Rate Limiting and Retry Logic

###### REQ-3.2.5.1 Rate Limit Detection
The system shall detect rate limiting responses from providers (HTTP 429 or provider-specific error codes).

###### REQ-3.2.5.2 Exponential Backoff
When rate limited, the system shall implement exponential backoff retry with configurable initial delay, maximum delay, and maximum retry attempts.

###### REQ-3.2.5.3 Retry on Transient Errors
The system shall automatically retry requests that fail due to transient errors (network timeouts, 5xx server errors) with configurable retry attempts.

###### REQ-3.2.5.4 Retry Logging
The system shall log all retry attempts including attempt number, reason for retry, and delay before next attempt.

---

#### REQ-3.3 Agentic System Integration

##### REQ-3.3.1 Agent Abstraction Interface
The system shall define an abstract interface for agentic systems that specifies required operations.

###### REQ-3.3.1.1 Task Submission Interface
The abstract interface shall define a method for submitting coding tasks to agents with parameters including task description, relevant file paths, permitted tools/operations, and termination conditions.

###### REQ-3.3.1.2 Result Retrieval Interface
The abstract interface shall define a method for retrieving agent results including generated code/modifications, tool calls executed, iteration count, and completion status.

###### REQ-3.3.1.3 Configuration Interface
The abstract interface shall define methods for configuring agent parameters including backend model selection, execution budget limits, and tool permissions.

##### REQ-3.3.2 Agent Adapter Implementations
The system shall provide adapter implementations or implementation stubs for common agentic systems.

###### REQ-3.3.2.1 Command-Line Agent Adapter
The system shall provide an adapter for agents that operate via command-line interface, supporting process invocation, stdin/stdout communication, and output parsing.

###### REQ-3.3.2.2 API-Based Agent Adapter
The system shall provide an adapter for agents that expose an API interface, supporting HTTP/gRPC communication and structured request/response handling.

###### REQ-3.3.2.3 Adapter Extension Points
The system shall document extension points for implementing additional agent adapters with code examples and interface specifications.

##### REQ-3.3.3 Agent Execution Environment

###### REQ-3.3.3.1 Sandbox Isolation
The system shall support execution of agents in isolated environments (containers or virtual machines) where applicable.

###### REQ-3.3.3.2 Resource Limits
The system shall enforce resource limits on agent execution including maximum wall-clock time, maximum CPU time, and maximum memory usage.

###### REQ-3.3.3.3 File System Access Control
The system shall restrict agent file system access to designated directories specified in task configuration.

##### REQ-3.3.4 Agent Telemetry Collection

###### REQ-3.3.4.1 Tool Usage Logging
The system shall log all tools invoked by agents including tool name, parameters, invocation timestamp, and result.

###### REQ-3.3.4.2 Iteration Tracking
The system shall track the number of iterations or reasoning steps executed by agents.

###### REQ-3.3.4.3 Resource Consumption Metrics
The system shall collect resource consumption metrics including execution time, token usage (if applicable), and peak memory usage.

---

#### REQ-3.4 Dataset Management

##### REQ-3.4.1 Dataset Discovery and Loading

###### REQ-3.4.1.1 Dataset Directory Structure Recognition
The system shall recognize dataset directory structures as defined in the COMET replication package including separate directories for requirements, source code, and ground truth files.

###### REQ-3.4.1.2 Dataset Metadata Loading
The system shall load dataset metadata including dataset name, programming language, lines of code count, and available link types (Rq→Src, UC→Src, Rq→Test).

###### REQ-3.4.1.3 Multi-Dataset Support
The system shall support loading and managing multiple datasets simultaneously (Albergate, EBT, LibEST, eTour, SMOS, iTrust).

##### REQ-3.4.2 Requirements File Parsing

###### REQ-3.4.2.1 Plain Text Requirements
The system shall parse plain text requirement files with one requirement per file, extracting requirement ID and requirement text.

###### REQ-3.4.2.2 Structured Requirements
The system shall parse structured requirement files (use cases) with template sections, extracting all sections as structured data.

###### REQ-3.4.2.3 Multi-Language Support
The system shall correctly handle requirements in multiple languages (English, Italian) with appropriate encoding (UTF-8).

##### REQ-3.4.3 Source Code File Loading

###### REQ-3.4.3.1 Source Code Discovery
The system shall discover all source code files in designated directories, recursing into subdirectories and filtering by file extension (e.g., .java, .c, .jsp).

###### REQ-3.4.3.2 Source Code Parsing
The system shall load source code files preserving original formatting and encoding.

###### REQ-3.4.3.3 Source Code Metadata Extraction
The system shall extract metadata from source code files including file path, file size, and line count.

##### REQ-3.4.4 Traceability Link Loading

###### REQ-3.4.4.1 Ground Truth File Parsing
The system shall parse ground truth files in space-separated format where each line contains requirement ID followed by linked artifact IDs.

###### REQ-3.4.4.2 Link Type Association
The system shall associate each link with its type (Rq→Src, UC→Src, Rq→Test) based on file naming or configuration.

###### REQ-3.4.4.3 Link Validation
The system shall validate that all linked artifacts exist in the loaded dataset and report any broken links.

##### REQ-3.4.5 Dataset Sampling

###### REQ-3.4.5.1 Random Sampling
The system shall support random sampling of requirements from datasets with configurable sample size and random seed for reproducibility.

###### REQ-3.4.5.2 Stratified Sampling
The system shall support stratified sampling based on link type or requirement complexity when such metadata is available.

###### REQ-3.4.5.3 Representative Sampling
The system shall support selection of representative requirements that span different source files and have varying link counts.

---

#### REQ-3.5 Experiment Execution Engine

##### REQ-3.5.1 Experiment Registry and Dispatch

###### REQ-3.5.1.1 Experiment Type Registration
The system shall maintain a registry of experiment types mapping experiment identifiers to implementation classes.

###### REQ-3.5.1.2 Dynamic Experiment Loading
The system shall dynamically load experiment implementations based on configuration without requiring code modification.

###### REQ-3.5.1.3 Experiment Dispatch
The system shall dispatch execution to appropriate experiment implementations based on configured experiment types.

##### REQ-3.5.2 Execution Orchestration Modes

###### REQ-3.5.2.1 Sequential Execution Mode
The system shall support sequential execution where experiments execute one after another in configured order.

###### REQ-3.5.2.2 Parallel Execution Mode
The system shall support parallel execution of independent experiments using configurable worker pools with maximum concurrency limits.

###### REQ-3.5.2.3 Selective Execution Mode
The system shall support selective execution where only specified experiments execute based on experiment IDs or tags provided in configuration or command-line.

###### REQ-3.5.2.4 Execution Mode Configuration
The system shall allow specification of execution mode in configuration file with values: 'sequential', 'parallel', or 'selective'.

##### REQ-3.5.3 Experiment State Management

###### REQ-3.5.3.1 State Persistence
The system shall persist experiment execution state to disk including experiments completed, experiments in progress, and experiments pending.

###### REQ-3.5.3.2 Resume Capability
The system shall support resuming execution from a previous state file, skipping already-completed experiments.

###### REQ-3.5.3.3 State File Format
The system shall store state in JSON format with schema including experiment ID, status (pending/running/completed/failed), start timestamp, end timestamp, and result file path.

###### REQ-3.5.3.4 State Locking
The system shall implement file locking on state files to prevent concurrent executions from corrupting state.

##### REQ-3.5.4 Progress Tracking and Reporting

###### REQ-3.5.4.1 Progress Logging
The system shall log progress updates including experiment started, experiment completed, estimated time remaining, and current experiment N of M total.

###### REQ-3.5.4.2 Progress Indicators
The system shall display progress indicators (progress bars or percentage) when executing in interactive mode.

###### REQ-3.5.4.3 Completion Notification
Upon completion of all experiments, the system shall log a summary including total experiments executed, successful experiments, failed experiments, and total execution time.

##### REQ-3.5.5 Error Handling and Recovery

###### REQ-3.5.5.1 Experiment-Level Error Isolation
The system shall isolate errors within individual experiments such that failure of one experiment does not terminate execution of remaining experiments.

###### REQ-3.5.5.2 Error Logging
The system shall log all errors with full stack traces and contextual information including experiment ID and parameters.

###### REQ-3.5.5.3 Failure Recovery Options
The system shall support configuration of failure behavior: continue (skip failed experiment), retry (with configurable retry count), or abort (terminate all execution).

---

#### REQ-3.6 Preliminary Experiment Implementations

##### REQ-3.6.1 Language Effect Assessment (Experiment Type 1)

###### REQ-3.6.1.1 Experiment Purpose
The system shall implement an experiment to assess the effect of requirement language (Italian vs. English) on model performance.

###### REQ-3.6.1.2 Dataset Selection
The experiment shall use requirements from Albergate and SMOS datasets (Italian originals) with corresponding English translations.

###### REQ-3.6.1.3 Model Selection
The experiment shall test 2-3 selected models on both language variants.

###### REQ-3.6.1.4 Task Definition
The experiment shall use a simple representative task from one of the TaskTypes (configurable).

###### REQ-3.6.1.5 Comparison Metrics
The experiment shall compute performance metrics for both language variants and calculate the difference.

###### REQ-3.6.1.6 Statistical Analysis
The experiment shall perform statistical tests (paired t-test or Wilcoxon) to determine if differences are significant.

###### REQ-3.6.1.7 Decision Output
The experiment shall output a recommendation: use Italian as-is, translate to English, or analyze separately.

##### REQ-3.6.2 Model Selection - Prompt-Based (Experiment Type 2)

###### REQ-3.6.2.1 Experiment Purpose
The system shall implement an experiment to select optimal prompt-based models from a candidate set.

###### REQ-3.6.2.2 Model Candidate Pool
The experiment shall test up to 10 candidate models (5 closed-source, 5 open-source) as configured.

###### REQ-3.6.2.3 Benchmark Task
The experiment shall execute a simple benchmark task consistently across all models including task description, input data, expected output format, and evaluation criteria.

###### REQ-3.6.2.4 Model Evaluation
The experiment shall evaluate each model on the benchmark task and record performance metrics (accuracy, speed, cost).

###### REQ-3.6.2.5 Model Ranking
The experiment shall rank models within each category (closed-source, open-source) based on composite performance score.

###### REQ-3.6.2.6 Model Selection
The experiment shall select the top 2 models from each category for use in main experiments.

###### REQ-3.6.2.7 Selection Documentation
The experiment shall generate a report documenting selection rationale including model rankings, performance metrics, and selection criteria.

##### REQ-3.6.3 Agent Selection and Backend Selection (Experiment Type 3)

###### REQ-3.6.3.1 Experiment Purpose
The system shall implement an experiment to select optimal agentic systems and their backend models.

###### REQ-3.6.3.2 Agent Candidate Pool
The experiment shall test 3-5 agentic systems per category (closed-source, open-source) as configured.

###### REQ-3.6.3.3 Backend Model Variation
For each agent, the experiment shall test multiple backend model options where applicable.

###### REQ-3.6.3.4 Agent Benchmark Task
The experiment shall execute a simple coding task consistently across all agents including task specification, permitted operations, and success criteria.

###### REQ-3.6.3.5 Agent Evaluation
The experiment shall evaluate each agent configuration (agent + backend) on benchmark metrics including task success rate, iteration count, tool usage, and execution time.

###### REQ-3.6.3.6 Agent Selection
The experiment shall select the top 2 agent configurations from each category.

###### REQ-3.6.3.7 Selection Documentation
The experiment shall generate a report documenting agent and backend selection with performance comparison tables.

##### REQ-3.6.4 Temperature Optimization (Experiment Type 4)

###### REQ-3.6.4.1 Experiment Purpose
The system shall implement an experiment to determine optimal temperature values for each TaskType.

###### REQ-3.6.4.2 Task Type Categorization
The experiment shall categorize tasks as correctness-critical (bug-fix, documentation) or exploratory (new-feature, test-generation).

###### REQ-3.6.4.3 Temperature Ranges
The experiment shall test temperatures [0.0, 0.1, 0.2] for correctness tasks and [0.5, 0.6, 0.7] for exploratory tasks.

###### REQ-3.6.4.4 Sample Task Execution
For each TaskType and temperature value, the experiment shall execute a sample of representative tasks.

###### REQ-3.6.4.5 Temperature Impact Analysis
The experiment shall analyze the impact of temperature on performance metrics specific to each TaskType.

###### REQ-3.6.4.6 Optimal Temperature Selection
The experiment shall select the temperature value that maximizes performance for each TaskType.

###### REQ-3.6.4.7 Temperature Configuration Output
The experiment shall output recommended temperature values per TaskType for use in main experiments.

##### REQ-3.6.5 Max Token Determination (Experiment Type 5)

###### REQ-3.6.5.1 Experiment Purpose
The system shall implement an experiment to determine appropriate max token limits for each TaskType.

###### REQ-3.6.5.2 Output Length Measurement
The experiment shall measure output lengths (in tokens) from sample task executions across TaskTypes.

###### REQ-3.6.5.3 Distribution Analysis
The experiment shall compute distribution statistics (mean, median, 95th percentile, maximum) of output lengths.

###### REQ-3.6.5.4 Truncation Risk Assessment
The experiment shall assess risk of output truncation at various token limits.

###### REQ-3.6.5.5 Max Token Recommendation
The experiment shall recommend either: no explicit limit (let provider determine) or specific limit per TaskType based on analysis.

###### REQ-3.6.5.6 Justification Documentation
The experiment shall document the rationale for max token recommendations.

##### REQ-3.6.6 Stop Sequence Definition (Experiment Type 6)

###### REQ-3.6.6.1 Experiment Purpose
The system shall implement an experiment to design and validate stop sequences for each TaskType.

###### REQ-3.6.6.2 Stop Sequence Design
For each TaskType, the experiment shall define candidate stop sequences based on expected output format.

###### REQ-3.6.6.3 Stop Sequence Testing
The experiment shall test stop sequences with sample outputs to verify correct truncation behavior.

###### REQ-3.6.6.4 False Positive Detection
The experiment shall detect cases where stop sequences incorrectly truncate valid output.

###### REQ-3.6.6.5 Stop Sequence Refinement
The experiment shall refine stop sequences based on testing results to minimize false positives while ensuring proper termination.

###### REQ-3.6.6.6 Stop Sequence Configuration Output
The experiment shall output validated stop sequences per TaskType for use in main experiments.

##### REQ-3.6.7 Prompting Strategy Testing (Experiment Type 7)

###### REQ-3.6.7.1 Experiment Purpose
The system shall implement an experiment to compare prompting strategies and select optimal approach.

###### REQ-3.6.7.2 Strategy Variants
The experiment shall test the following prompting strategies: zero-shot, zero-shot with chain-of-thought, and optionally few-shot with chain-of-thought.

###### REQ-3.6.7.3 Prompt Template Creation
For each strategy, the experiment shall create prompt templates incorporating: persona, task instruction, requirement/use case, and output format specification.

###### REQ-3.6.7.4 Strategy Comparison
The experiment shall execute sample tasks with each prompting strategy and compare performance metrics.

###### REQ-3.6.7.5 Strategy Selection
The experiment shall select the prompting strategy with best overall performance (expected: zero-shot + chain-of-thought).

###### REQ-3.6.7.6 Strategy Documentation
The experiment shall document the selected strategy with example prompts for each TaskType.

##### REQ-3.6.8 Control Condition Data Determination (Experiment Type 8)

###### REQ-3.6.8.1 Experiment Purpose
The system shall implement an experiment to determine appropriate control condition data (no traceability links).

###### REQ-3.6.8.2 Control Variant Design
The experiment shall test control variants: full codebase access and expanded file list (broader than treatment but not complete).

###### REQ-3.6.8.3 Model Type Separation
The experiment shall test control variants separately for prompt-based and agentic models.

###### REQ-3.6.8.4 Variant Comparison
The experiment shall compare control variants on sample tasks measuring: task completion rate, correctness, and execution time.

###### REQ-3.6.8.5 Control Selection
The experiment shall select the control variant that provides meaningful comparison without being functionally equivalent to treatment.

###### REQ-3.6.8.6 Control Configuration Output
The experiment shall output recommended control condition configuration per model type.

##### REQ-3.6.9 Token Budget Allocation (Experiment Type 9)

###### REQ-3.6.9.1 Experiment Purpose
The system shall implement an experiment to determine optimal token budget allocation across prompt sections.

###### REQ-3.6.9.2 Section Token Measurement
The experiment shall measure typical token counts for each prompt section: persona, instruction, requirement, traceability bundle, file list, and output specification.

###### REQ-3.6.9.3 Allocation Scheme Design
The experiment shall design allocation schemes (e.g., 25% instruction, 25% requirement, 50% context) with absolute token limits per section.

###### REQ-3.6.9.4 Truncation Testing
The experiment shall test allocation schemes with real data to verify no critical information is truncated.

###### REQ-3.6.9.5 Adjustment and Validation
The experiment shall adjust allocation if truncation occurs and re-validate.

###### REQ-3.6.9.6 Budget Configuration Output
The experiment shall output finalized token budget allocation scheme per prompt section.

##### REQ-3.6.10 Power Analysis (Experiment Type 10)

###### REQ-3.6.10.1 Experiment Purpose
The system shall implement an experiment to conduct statistical power analysis determining required sample sizes.

###### REQ-3.6.10.2 Variance Estimation
The experiment shall collect pilot data for all TaskTypes and compute variance estimates for Δ scores (treatment - control).

###### REQ-3.6.10.3 Effect Size Definition
The experiment shall define minimum practically significant effect sizes per TaskType based on domain knowledge or pilot observations.

###### REQ-3.6.10.4 Power Calculation
For each TaskType, the experiment shall calculate required sample size to achieve power = 0.80 at α = 0.05 for detecting the specified effect size.

###### REQ-3.6.10.5 Inflation Factor
The experiment shall apply an inflation factor (e.g., 10-20%) to account for unusable runs (failures, timeouts).

###### REQ-3.6.10.6 Sample Size Output
The experiment shall output recommended sample sizes per TaskType for main experiments.

---

#### REQ-3.7 Data Storage and Management

##### REQ-3.7.1 Result Storage Format

###### REQ-3.7.1.1 Structured Result Files
The system shall store experiment results in structured format (JSON) with schema including experiment metadata, input parameters, model outputs, computed metrics, and timestamps.

###### REQ-3.7.1.2 Raw Output Preservation
The system shall preserve raw LLM outputs without modification alongside processed results.

###### REQ-3.7.1.3 File Naming Convention
The system shall use consistent file naming convention: `{experiment_type}_{experiment_id}_{timestamp}.json`

##### REQ-3.7.2 CSV Export

###### REQ-3.7.2.1 Tabular Data Export
The system shall export experiment results to CSV format with one row per experiment run.

###### REQ-3.7.2.2 Column Schema
CSV files shall include columns for: experiment_id, experiment_type, model_id, input_parameters (JSON string), output_metrics (expandable), execution_time, timestamp.

###### REQ-3.7.2.3 Multi-File Export
The system shall support exporting different experiment types to separate CSV files or consolidated into single file.

##### REQ-3.7.3 Metadata Tracking

###### REQ-3.7.3.1 Execution Metadata
The system shall record execution metadata for each experiment including start time, end time, execution duration, system information (OS, Python version), and configuration hash.

###### REQ-3.7.3.2 Model Metadata
The system shall record model metadata including provider, model version/identifier, API endpoint used, and parameter settings.

###### REQ-3.7.3.3 Dataset Metadata
The system shall record dataset metadata including dataset name, version/commit hash if available, and file paths used.

##### REQ-3.7.4 Data Versioning

###### REQ-3.7.4.1 Result Versioning
The system shall maintain version information for result files to track changes in experiment implementations or configurations.

###### REQ-3.7.4.2 Backward Compatibility
The system shall maintain backward compatibility to read result files from previous versions.

###### REQ-3.7.4.3 Migration Support
The system shall provide migration utilities to upgrade old result formats to current schema.

---

#### REQ-3.8 Analysis and Reporting

##### REQ-3.8.1 Statistical Analysis Engine

###### REQ-3.8.1.1 Descriptive Statistics
The system shall compute descriptive statistics for all metrics including mean, median, standard deviation, min, max, and quartiles.

###### REQ-3.8.1.2 Comparative Statistics
The system shall compute comparative statistics between conditions including paired differences, effect sizes (Cohen's d, Cliff's Delta), and confidence intervals.

###### REQ-3.8.1.3 Hypothesis Testing
The system shall perform hypothesis tests as appropriate including paired t-tests, Wilcoxon signed-rank tests, and ANOVA where applicable.

###### REQ-3.8.1.4 Power Analysis Computation
The system shall compute statistical power for given sample sizes and effect sizes using established formulas or libraries.

###### REQ-3.8.1.5 Correlation Analysis
The system shall compute correlation coefficients (Pearson, Spearman) between variables when analyzing relationships.

##### REQ-3.8.2 Report Generation

###### REQ-3.8.2.1 Report Format Support
The system shall generate reports in the following formats: Markdown (.md), HTML (.html), PDF (.pdf), and CSV (.csv).

###### REQ-3.8.2.2 Report Templates
The system shall support customizable report templates for each output format with placeholders for dynamic content.

###### REQ-3.8.2.3 Report Content Sections
Reports shall include the following sections: executive summary, experiment configuration, results summary tables, statistical analysis results, visualizations (where applicable), and detailed results appendix.

##### REQ-3.8.3 Markdown Report Generation

###### REQ-3.8.3.1 Markdown Structure
The system shall generate Markdown reports with proper heading hierarchy, tables, and code blocks.

###### REQ-3.8.3.2 Markdown Tables
The system shall format tabular data as Markdown tables with proper alignment and formatting.

###### REQ-3.8.3.3 Markdown Formatting
The system shall use Markdown formatting for emphasis (bold, italic) and lists as appropriate.

##### REQ-3.8.4 HTML Report Generation

###### REQ-3.8.4.1 HTML Structure
The system shall generate valid HTML5 documents with proper DOCTYPE, head, and body sections.

###### REQ-3.8.4.2 HTML Styling
The system shall include CSS styling for professional appearance with responsive design principles.

###### REQ-3.8.4.3 HTML Tables
The system shall render tables with sortable columns and hover effects where applicable.

###### REQ-3.8.4.4 HTML Interactive Elements
The system shall support interactive elements in HTML reports including collapsible sections and tabbed content.

##### REQ-3.8.5 PDF Report Generation

###### REQ-3.8.5.1 PDF Rendering
The system shall generate PDF reports from HTML or Markdown using a PDF rendering library (e.g., WeasyPrint, ReportLab).

###### REQ-3.8.5.2 PDF Page Layout
The system shall use appropriate page layout with headers, footers, and page numbers.

###### REQ-3.8.5.3 PDF Typography
The system shall use professional fonts and appropriate font sizes for readability.

###### REQ-3.8.5.4 PDF Table of Contents
The system shall generate a table of contents with page number references for PDF reports.

##### REQ-3.8.6 Visualization Generation

###### REQ-3.8.6.1 Plot Types
The system shall generate visualizations including bar charts (for comparisons), line plots (for trends), box plots (for distributions), and scatter plots (for correlations).

###### REQ-3.8.6.2 Plot Formatting
The system shall format plots with appropriate labels (title, axis labels, legend), colors, and sizing.

###### REQ-3.8.6.3 Plot Export
The system shall export plots in multiple formats including PNG (for documents) and SVG (for scalability).

###### REQ-3.8.6.4 Plot Embedding
The system shall embed generated plots in HTML and PDF reports.

##### REQ-3.8.7 Summary Statistics Tables

###### REQ-3.8.7.1 Per-Experiment Summary
The system shall generate summary tables showing key metrics for each experiment run.

###### REQ-3.8.7.2 Aggregate Summary
The system shall generate aggregate summary tables across multiple runs of the same experiment type.

###### REQ-3.8.7.3 Comparison Tables
The system shall generate comparison tables showing side-by-side metrics for different conditions or models.

---

#### REQ-3.9 Logging and Monitoring

##### REQ-3.9.1 Logging Infrastructure

###### REQ-3.9.1.1 Logging Framework
The system shall use Python's standard logging framework for all logging operations.

###### REQ-3.9.1.2 Log Levels
The system shall support standard log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL with configurable minimum level.

###### REQ-3.9.1.3 Log Output Destinations
The system shall support logging to: console (stdout/stderr), file (rotating file handler), and optionally remote logging services.

###### REQ-3.9.1.4 Log Format
The system shall format log messages with: timestamp, log level, module name, and message.

##### REQ-3.9.2 Experiment Logging

###### REQ-3.9.2.1 Experiment Lifecycle Logging
The system shall log key events in experiment lifecycle including experiment started, parameters loaded, model invoked, response received, metrics computed, and experiment completed.

###### REQ-3.9.2.2 Error Logging
The system shall log all errors with full exception details including stack trace and context information.

###### REQ-3.9.2.3 Warning Logging
The system shall log warnings for non-fatal issues including configuration deprecations, missing optional parameters, and performance concerns.

##### REQ-3.9.3 Performance Monitoring

###### REQ-3.9.3.1 Execution Time Tracking
The system shall track and log execution time for each experiment and for the overall execution.

###### REQ-3.9.3.2 Resource Usage Monitoring
The system shall monitor and log resource usage including memory consumption and API call counts.

###### REQ-3.9.3.3 Performance Metrics
The system shall compute performance metrics including average time per experiment, throughput (experiments per minute), and API response times.

##### REQ-3.9.4 Audit Trail

###### REQ-3.9.4.1 Configuration Audit
The system shall log the complete configuration used for each execution including configuration file path and hash of configuration content.

###### REQ-3.9.4.2 Command Audit
The system shall log the complete command line invocation including all arguments and overrides.

###### REQ-3.9.4.3 Result Audit
The system shall log the location of all generated result files and reports.

---

#### REQ-3.10 Command-Line Interface

##### REQ-3.10.1 CLI Structure

###### REQ-3.10.1.1 Command Syntax
The system shall provide a command-line interface with syntax: `prelim-exp <command> [options]`

###### REQ-3.10.1.2 Available Commands
The system shall support the following commands: run (execute experiments), validate (validate configuration), analyze (analyze existing results), report (generate reports), and list (list available experiments).

###### REQ-3.10.1.3 Help System
The system shall provide comprehensive help text for each command accessible via `--help` flag.

##### REQ-3.10.2 Common Options

###### REQ-3.10.2.1 Configuration File Option
The system shall accept a configuration file path via `--config` or `-c` option.

###### REQ-3.10.2.2 Verbosity Option
The system shall accept a verbosity level via `--verbose` or `-v` option (multiple uses increase verbosity).

###### REQ-3.10.2.3 Output Directory Option
The system shall accept an output directory path via `--output` or `-o` option.

###### REQ-3.10.2.4 Dry Run Option
The system shall support a dry-run mode via `--dry-run` flag that validates configuration without executing experiments.

##### REQ-3.10.3 Run Command

###### REQ-3.10.3.1 Experiment Selection
The run command shall accept experiment IDs to execute via `--experiments` option (comma-separated list).

###### REQ-3.10.3.2 Execution Mode
The run command shall accept execution mode via `--mode` option with values: sequential, parallel, selective.

###### REQ-3.10.3.3 Resume Option
The run command shall accept a `--resume` flag to continue from previous execution state.

###### REQ-3.10.3.4 No-Cache Option
The run command shall accept a `--no-cache` flag to force re-execution of all experiments regardless of cache state.

##### REQ-3.10.4 Validate Command

###### REQ-3.10.4.1 Configuration Validation
The validate command shall check configuration file syntax and schema compliance.

###### REQ-3.10.4.2 Dataset Validation
The validate command shall check that specified datasets exist and are readable.

###### REQ-3.10.4.3 Model Validation
The validate command shall check that model configurations are valid (without making API calls).

###### REQ-3.10.4.4 Validation Report
The validate command shall output a validation report indicating pass/fail for each check.

##### REQ-3.10.5 Analyze Command

###### REQ-3.10.5.1 Result Loading
The analyze command shall load results from specified directory or from default output location.

###### REQ-3.10.5.2 Analysis Type Selection
The analyze command shall accept analysis type via `--analysis` option: descriptive, comparative, power.

###### REQ-3.10.5.3 Filter Options
The analyze command shall accept filters to analyze subset of results via `--filter` option.

##### REQ-3.10.6 Report Command

###### REQ-3.10.6.1 Format Selection
The report command shall accept output format via `--format` option: markdown, html, pdf, csv, all.

###### REQ-3.10.6.2 Template Selection
The report command shall accept report template via `--template` option.

###### REQ-3.10.6.3 Output Path
The report command shall accept output file path via `--output` option.

##### REQ-3.10.7 List Command

###### REQ-3.10.7.1 Experiment Listing
The list command with `--experiments` flag shall list all available experiment types with descriptions.

###### REQ-3.10.7.2 Model Listing
The list command with `--models` flag shall list all configured models.

###### REQ-3.10.7.3 Dataset Listing
The list command with `--datasets` flag shall list all configured datasets with metadata.

---

### 3.2 NON-FUNCTIONAL REQUIREMENTS

#### REQ-3.2.1 Performance Requirements

##### REQ-3.2.1.1 Execution Efficiency
The system shall minimize overhead such that experiment execution time is dominated by LLM API response time, not system processing.

##### REQ-3.2.1.2 Memory Management
The system shall manage memory efficiently to handle large datasets and results without excessive memory consumption (target: < 2 GB for typical workload).

##### REQ-3.2.1.3 Parallel Execution Scaling
When executing in parallel mode, the system shall achieve near-linear scaling up to the configured concurrency limit.

##### REQ-3.2.1.4 File I/O Optimization
The system shall optimize file I/O operations through appropriate buffering and lazy loading strategies.

#### REQ-3.2.2 Reliability Requirements

##### REQ-3.2.2.1 Error Tolerance
The system shall tolerate transient errors (network failures, temporary API unavailability) through automatic retry mechanisms.

##### REQ-3.2.2.2 Data Integrity
The system shall ensure data integrity through atomic file operations and proper exception handling.

##### REQ-3.2.2.3 State Consistency
The system shall maintain consistent state even in the presence of interruptions (SIGINT, SIGTERM).

##### REQ-3.2.2.4 Graceful Degradation
The system shall degrade gracefully when optional features are unavailable (e.g., PDF generation without required libraries).

#### REQ-3.2.3 Maintainability Requirements

##### REQ-3.2.3.1 Code Modularity
The system shall organize code into modules with clear responsibilities and minimal coupling.

##### REQ-3.2.3.2 Code Documentation
The system shall include comprehensive docstrings for all public classes and functions following PEP 257 conventions.

##### REQ-3.2.3.3 Type Hints
The system shall use Python type hints for all function signatures to enable static type checking.

##### REQ-3.2.3.4 Unit Test Coverage
The system shall include unit tests with minimum 80% code coverage for core functionality.

#### REQ-3.2.4 Portability Requirements

##### REQ-3.2.4.1 Cross-Platform Compatibility
The system shall run without modification on Linux, macOS, and Windows platforms.

##### REQ-3.2.4.2 Python Version Support
The system shall support Python versions 3.9, 3.10, 3.11, and 3.12.

##### REQ-3.2.4.3 Dependency Management
The system shall specify all dependencies with version ranges that ensure compatibility.

##### REQ-3.2.4.4 Path Handling
The system shall use platform-independent path handling (pathlib) for all file operations.

#### REQ-3.2.5 Security Requirements

##### REQ-3.2.5.1 Credential Protection
The system shall not log, print, or store API credentials in plain text outside of configuration files.

##### REQ-3.2.5.2 Configuration File Permissions
The system shall check and warn if configuration files containing credentials have overly permissive file permissions.

##### REQ-3.2.5.3 Input Validation
The system shall validate all user inputs and configuration values to prevent injection attacks.

##### REQ-3.2.5.4 Secure Communication
The system shall use HTTPS for all API communications and validate SSL certificates.

#### REQ-3.2.6 Usability Requirements

##### REQ-3.2.6.1 Clear Error Messages
The system shall provide clear, actionable error messages that guide users toward resolution.

##### REQ-3.2.6.2 Configuration Examples
The system shall provide example configuration files demonstrating common use cases.

##### REQ-3.2.6.3 Progress Feedback
The system shall provide real-time progress feedback during long-running operations.

##### REQ-3.2.6.4 Documentation Completeness
The system shall include comprehensive user documentation covering installation, configuration, execution, and troubleshooting.

---

## 4. VERIFICATION AND VALIDATION

### 4.1 Verification Methods

#### REQ-4.1.1 Requirements Traceability
All requirements shall be traceable to test cases that verify their implementation.

#### REQ-4.1.2 Unit Testing
All individual functions and classes shall be verified through unit tests that exercise normal and edge cases.

#### REQ-4.1.3 Integration Testing
Integration between components shall be verified through integration tests that exercise component interactions.

#### REQ-4.1.4 System Testing
Complete workflows shall be verified through end-to-end system tests.

### 4.2 Validation Methods

#### REQ-4.2.1 Configuration Validation
Configuration file parsing and validation shall be validated against valid and invalid configuration examples.

#### REQ-4.2.2 Experiment Execution Validation
Each experiment type shall be validated by executing with sample data and verifying expected outputs.

#### REQ-4.2.3 Report Generation Validation
Report generation shall be validated by inspecting generated reports in all formats for correctness and completeness.

#### REQ-4.2.4 User Acceptance Testing
The system shall undergo user acceptance testing by the research scientist to validate fitness for purpose.

---

## 5. APPENDICES

### 5.1 Acronyms and Abbreviations

- **API**: Application Programming Interface
- **CLI**: Command-Line Interface
- **CoT**: Chain of Thought
- **CSV**: Comma-Separated Values
- **HTML**: HyperText Markup Language
- **HTTP**: HyperText Transfer Protocol
- **HTTPS**: HTTP Secure
- **JSON**: JavaScript Object Notation
- **LLM**: Large Language Model
- **LoC**: Lines of Code
- **PDF**: Portable Document Format
- **PES**: Preliminary Experiments System
- **REST**: Representational State Transfer
- **SDK**: Software Development Kit
- **URL**: Uniform Resource Locator
- **YAML**: YAML Ain't Markup Language

### 5.2 Glossary

- **Agentic System**: An autonomous software system that uses LLMs to perform multi-step reasoning and tool usage.
- **Chain of Thought**: A prompting technique that encourages the LLM to show its reasoning process.
- **Control Condition**: Experimental condition without traceability data provided.
- **Effect Size**: A quantitative measure of the magnitude of a phenomenon.
- **Ground Truth**: Manually verified correct answers used for evaluation.
- **Prompt**: Text input provided to an LLM to elicit a response.
- **Task Instance**: A specific instantiation of a coding task with concrete inputs.
- **TaskType**: Category of coding task (new feature, bug fix, test generation, documentation).
- **Temperature**: LLM parameter controlling randomness of outputs (0 = deterministic, higher = more random).
- **Token**: Unit of text processed by LLMs (roughly 0.75 words in English).
- **Traceability Link**: Association between a requirement and implementation artifact.
- **Treatment Condition**: Experimental condition with traceability data provided.

### 5.3 Requirements Traceability Matrix

The complete requirements traceability matrix mapping requirements to test cases shall be maintained separately and updated as implementation progresses.

---

## DOCUMENT APPROVAL

This requirements specification shall be reviewed and approved by:

- **Research Lead**: [Name, Date, Signature]
- **Software Developer**: [Name, Date, Signature]
- **Quality Assurance**: [Name, Date, Signature]

---

**END OF REQUIREMENTS SPECIFICATION**