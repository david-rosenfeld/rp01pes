# Integration Checklist - Dataset Management Module

## ✅ Step-by-Step Integration

### 1. Download Files from Claude
- [ ] Download the `datasets/` folder
- [ ] Download `test_datasets.py`
- [ ] Download documentation files

### 2. Copy to Your Project
```bash
# From your download location:
cp -r datasets/ /path/to/your/project/pes/
cp test_datasets.py /path/to/your/project/
```

### 3. Verify File Structure
```
your-project/
├── pes/
│   ├── core/           (already exists)
│   ├── llm/            (already exists)
│   ├── datasets/       ← NEW
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── ground_truth.py
│   │   ├── loader.py
│   │   ├── traceability.py
│   │   └── README.md
│   └── experiments/    (already exists)
├── datasets/           (your COMET data)
│   ├── Albergate/
│   ├── EBT/
│   ├── LibEST/
│   ├── eTOUR/
│   ├── SMOS/
│   └── iTrust/
├── test_datasets.py    ← NEW
└── configs/config.yaml (already exists)
```

### 4. Test the Installation
```bash
cd /path/to/your/project
python test_datasets.py
```

Expected output:
```
======================================================================
DATASET MANAGEMENT MODULE TEST
======================================================================

Test 1: List Available Datasets
----------------------------------------------------------------------
Available datasets: albergate, ebt, libest, etour, smos, itrust
Total: 6 datasets

...

======================================================================
ALL TESTS COMPLETED SUCCESSFULLY! ✓
======================================================================
```

### 5. Update Configuration (Optional)
Add to `configs/config.yaml`:
```yaml
datasets:
  base_path: "./datasets"
  
  # Token budget settings (from PE09 results later)
  token_budget:
    requirement: 2400
    traceability: 2800
    total: 5200
```

### 6. Try It in Python REPL
```python
from pes.datasets import load_dataset, generate_bundles_for_dataset

# Load a dataset
dataset = load_dataset('albergate', {'base_path': './datasets'})
print(f"Loaded {len(dataset.requirements)} requirements")

# Generate bundles
bundles = generate_bundles_for_dataset(dataset, token_budget=5000)
print(f"Generated {len(bundles)} bundles")

# Success! 🎉
```

### 7. Use in an Experiment

Update an experiment file (e.g., `pe01.py`):
```python
from pes.datasets import load_dataset, generate_bundles_for_dataset

# In your experiment's run() method:
def run(self):
    # Load datasets
    albergate = load_dataset('albergate', self.config['datasets'])
    
    # Generate bundles
    bundles = generate_bundles_for_dataset(albergate)
    
    # Use bundles...
    for req_id, bundle in bundles.items():
        # Your experiment logic here
        pass
```

## 🔍 Troubleshooting

### Problem: Import Error
```
ModuleNotFoundError: No module named 'pes.datasets'
```
**Solution**: 
- Verify `datasets/` folder is in `pes/` directory
- Check that `pes/datasets/__init__.py` exists
- Run from project root directory

### Problem: Dataset Not Found
```
DatasetError: Dataset directory not found: ./datasets/Albergate
```
**Solution**: 
- Verify your datasets are in `./datasets/` directory
- Check folder names match exactly (case-sensitive)
- Update `base_path` in config if datasets are elsewhere

### Problem: Test Script Fails
```
Test 2: Load All Datasets - FAILED
```
**Solution**: 
- Check that ALL 6 COMET datasets are downloaded
- Verify directory structure matches expected format
- See warnings in test output for specific issues

## 📋 Verification Checklist

After integration, verify:

- [ ] `python test_datasets.py` runs successfully
- [ ] All 6 datasets load without errors
- [ ] Can import: `from pes.datasets import load_dataset`
- [ ] Can generate bundles without errors
- [ ] Italian text displays correctly (no encoding errors)
- [ ] Log files are created in `logs/` directory

## 🎯 Next Steps After Integration

1. **Implement Real LLM Providers**
   - So experiments can call actual APIs
   - Priority: OpenAI, then Anthropic

2. **Complete PE01 Experiment**
   - Use datasets for language effect testing
   - First experiment with real data

3. **Add Statistical Analysis**
   - Implement hypothesis tests
   - Calculate effect sizes

4. **Complete Other Experiments**
   - PE04, PE07, PE10, etc.
   - All can now use real datasets

## 📚 Documentation References

- **User Guide**: `pes/datasets/README.md`
- **Architecture**: `ARCHITECTURE.md` (in project)
- **Implementation**: `DATASET_MODULE_SUMMARY.md`
- **Code Examples**: `test_datasets.py`

## 🎉 Success Criteria

You've successfully integrated the module when:

✅ Test script runs to completion
✅ Can load all 6 datasets in Python
✅ Can generate traceability bundles
✅ No import or path errors
✅ Ready to use in experiments

---

**Questions?** Review the documentation files or test script for examples!
