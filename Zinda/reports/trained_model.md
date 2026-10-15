# Trained matcher card

**Artifact:** `models/tcpd_linkage.joblib`  
**Version:** `tcpd-mlp-17epoch-v1`  
**Model:** MLP with hidden layers (64, 32), trained for up to 17 epochs.  
**Training data:** TCPD Indian election candidates; no voter or pension records used for fitting.

The person-level holdout keeps each `pid` entirely in train or test. Positives are different records sharing a `pid`; hard negatives are different `pid`s from the same normalized state and sharing at least one name token of 3+ characters. Positive pairs are sampled uniformly up to 10,000 per split, and negatives up to 1.5 per positive. Training uses a maximum of 17 full passes (epochs) over the training pairs, without early stopping.

Held-out identities: 22,142. Held-out pairs: 25,000 (10,000 positive, 15,000 hard negative).
AP: 0.986; ROC AUC: 0.992; thresholded precision: 0.965; recall: 0.933; F1: 0.948.
The training-only F1 threshold is `0.6038`. It is a demo review-routing threshold, not calibrated for a field population.

## Limits

These figures apply only to this constructed TCPD candidate-pair pool. TCPD is not representative of pension beneficiaries, and hard negatives are sampled rather than exhaustive. The model score is not a real-world match probability. It cannot confirm identity, death, eligibility, or wrongful removal; use it only to order records for a human reviewer.
