AISTAP subset leave-one-subset-out cross-condition evaluation
Root: C:\Users\刘子轩\Desktop\TP-SSCS项目
Subsets: simMed, simNoiseOnly, simWind
Seeds: 7, 11, 23
Hyperparams: rank=30, hidden=16, steps=150, lr=0.02

Dataset balance:
- simMed: 2 images
- simNoiseOnly: 2 images
- simWind: 2 images

Hold-out summary at test time:
- holdout=simMed method=low_rank_residual pfa=1e-04 Pd=0.2326±0.0000 Pfa=0.0001±0.0000
- holdout=simMed method=low_rank_residual pfa=1e-03 Pd=0.7674±0.0000 Pfa=0.0010±0.0000
- holdout=simMed method=low_rank_residual pfa=1e-02 Pd=0.9535±0.0000 Pfa=0.0100±0.0000
- holdout=simMed method=raw pfa=1e-04 Pd=0.0930±0.0000 Pfa=0.0001±0.0000
- holdout=simMed method=raw pfa=1e-03 Pd=0.2326±0.0000 Pfa=0.0010±0.0000
- holdout=simMed method=raw pfa=1e-02 Pd=0.4651±0.0000 Pfa=0.0100±0.0000
- holdout=simMed method=trainable_gate pfa=1e-04 Pd=0.1589±0.0947 Pfa=0.0001±0.0000
- holdout=simMed method=trainable_gate pfa=1e-03 Pd=0.4922±0.1997 Pfa=0.0010±0.0000
- holdout=simMed method=trainable_gate pfa=1e-02 Pd=0.8178±0.2169 Pfa=0.0100±0.0000
- holdout=simNoiseOnly method=low_rank_residual pfa=1e-04 Pd=0.4419±0.0000 Pfa=0.0001±0.0000
- holdout=simNoiseOnly method=low_rank_residual pfa=1e-03 Pd=0.7442±0.0000 Pfa=0.0010±0.0000
- holdout=simNoiseOnly method=low_rank_residual pfa=1e-02 Pd=0.8605±0.0000 Pfa=0.0100±0.0000
- holdout=simNoiseOnly method=raw pfa=1e-04 Pd=0.2093±0.0000 Pfa=0.0001±0.0000
- holdout=simNoiseOnly method=raw pfa=1e-03 Pd=0.7674±0.0000 Pfa=0.0010±0.0000
- holdout=simNoiseOnly method=raw pfa=1e-02 Pd=0.8837±0.0000 Pfa=0.0100±0.0000
- holdout=simNoiseOnly method=trainable_gate pfa=1e-04 Pd=0.3798±0.1037 Pfa=0.0001±0.0000
- holdout=simNoiseOnly method=trainable_gate pfa=1e-03 Pd=0.7597±0.0190 Pfa=0.0010±0.0000
- holdout=simNoiseOnly method=trainable_gate pfa=1e-02 Pd=0.8682±0.0120 Pfa=0.0100±0.0000
- holdout=simWind method=low_rank_residual pfa=1e-04 Pd=0.1628±0.0000 Pfa=0.0001±0.0000
- holdout=simWind method=low_rank_residual pfa=1e-03 Pd=0.8140±0.0000 Pfa=0.0010±0.0000
- holdout=simWind method=low_rank_residual pfa=1e-02 Pd=0.9070±0.0000 Pfa=0.0100±0.0000
- holdout=simWind method=raw pfa=1e-04 Pd=0.0930±0.0000 Pfa=0.0001±0.0000
- holdout=simWind method=raw pfa=1e-03 Pd=0.3023±0.0000 Pfa=0.0010±0.0000
- holdout=simWind method=raw pfa=1e-02 Pd=0.5349±0.0000 Pfa=0.0100±0.0000
- holdout=simWind method=trainable_gate pfa=1e-04 Pd=0.2093±0.0964 Pfa=0.0001±0.0000
- holdout=simWind method=trainable_gate pfa=1e-03 Pd=0.6085±0.1724 Pfa=0.0010±0.0000
- holdout=simWind method=trainable_gate pfa=1e-02 Pd=0.8295±0.1719 Pfa=0.0100±0.0000

Snapshot summary:
- holdout=simMed seed=7 split=test step=0 loss=0.7505 gate_gap=-0.0708
- holdout=simMed seed=7 split=test step=150 loss=0.0160 gate_gap=0.8682
- holdout=simMed seed=7 split=train step=0 loss=0.6686 gate_gap=-0.0456
- holdout=simMed seed=7 split=train step=150 loss=0.0338 gate_gap=0.7273
- holdout=simMed seed=11 split=test step=0 loss=0.9678 gate_gap=0.0053
- holdout=simMed seed=11 split=test step=150 loss=0.0073 gate_gap=0.9364
- holdout=simMed seed=11 split=train step=0 loss=1.0064 gate_gap=0.0100
- holdout=simMed seed=11 split=train step=150 loss=0.0220 gate_gap=0.8233
- holdout=simMed seed=23 split=test step=0 loss=1.0184 gate_gap=0.0392
- holdout=simMed seed=23 split=test step=150 loss=0.0064 gate_gap=0.9574
- holdout=simMed seed=23 split=train step=0 loss=1.1123 gate_gap=0.0240
- holdout=simMed seed=23 split=train step=150 loss=0.0240 gate_gap=0.8020
- holdout=simNoiseOnly seed=7 split=test step=0 loss=0.5934 gate_gap=-0.0259
- holdout=simNoiseOnly seed=7 split=test step=150 loss=0.2111 gate_gap=0.1632
- holdout=simNoiseOnly seed=7 split=train step=0 loss=0.7471 gate_gap=-0.0681
- holdout=simNoiseOnly seed=7 split=train step=150 loss=0.0019 gate_gap=0.9813
- holdout=simNoiseOnly seed=11 split=test step=0 loss=1.0463 gate_gap=0.0118
- holdout=simNoiseOnly seed=11 split=test step=150 loss=0.1433 gate_gap=0.1815
- holdout=simNoiseOnly seed=11 split=train step=0 loss=0.9671 gate_gap=0.0067
- holdout=simNoiseOnly seed=11 split=train step=150 loss=0.0033 gate_gap=0.9709
- holdout=simNoiseOnly seed=23 split=test step=0 loss=1.2009 gate_gap=0.0108
- holdout=simNoiseOnly seed=23 split=test step=150 loss=0.2088 gate_gap=0.2250
- holdout=simNoiseOnly seed=23 split=train step=0 loss=1.0210 gate_gap=0.0382
- holdout=simNoiseOnly seed=23 split=train step=150 loss=0.0022 gate_gap=0.9801
- holdout=simWind seed=7 split=test step=0 loss=0.7438 gate_gap=-0.0654
- holdout=simWind seed=7 split=test step=150 loss=0.0093 gate_gap=0.9211
- holdout=simWind seed=7 split=train step=0 loss=0.6719 gate_gap=-0.0483
- holdout=simWind seed=7 split=train step=150 loss=0.0168 gate_gap=0.8803
- holdout=simWind seed=11 split=test step=0 loss=0.9665 gate_gap=0.0081
- holdout=simWind seed=11 split=test step=150 loss=0.0264 gate_gap=0.5006
- holdout=simWind seed=11 split=train step=0 loss=1.0071 gate_gap=0.0086
- holdout=simWind seed=11 split=train step=150 loss=0.0350 gate_gap=0.4806
- holdout=simWind seed=23 split=test step=0 loss=1.0237 gate_gap=0.0372
- holdout=simWind seed=23 split=test step=150 loss=0.0099 gate_gap=0.9130
- holdout=simWind seed=23 split=train step=0 loss=1.1096 gate_gap=0.0250
- holdout=simWind seed=23 split=train step=150 loss=0.0169 gate_gap=0.8606
