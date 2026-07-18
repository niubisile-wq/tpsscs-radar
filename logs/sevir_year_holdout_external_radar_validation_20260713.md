SEVIR year-holdout external radar validation
Root: C:\sevir1
Max per file: 96

Feature set:
 - episode max/mean/std
 - fraction above 20/40/60
 - per-frame max mean/std
 - per-frame mean mean/std

Selected model: mlp
Validation threshold from 2018: 0.5496

Test 2019 AUC=0.4817
Test 2019 raw-AUC(on f0)=0.4859
Test 2019 raw-AUC(on f1)=0.4737
Test 2019 balanced-acc@val-threshold=0.5019
Test 2019 raw-best-bal-acc=0.5005
Test 2019 prob-best-bal-acc=0.5099

Candidate model sweep:
- mlp: val_auc=0.5008 val_bal_acc=0.5185 test_auc=0.4817 test_bal_acc(best=0.5099)
- logreg: val_auc=0.5000 val_bal_acc=0.5000 test_auc=0.5000 test_bal_acc(best=0.5000)
- gbdt: val_auc=0.5000 val_bal_acc=0.5000 test_auc=0.5000 test_bal_acc(best=0.5000)
- rf: val_auc=0.5000 val_bal_acc=0.5000 test_auc=0.5216 test_bal_acc(best=0.5578)
- extra_trees: val_auc=0.5000 val_bal_acc=0.5000 test_auc=0.5000 test_bal_acc(best=0.5000)