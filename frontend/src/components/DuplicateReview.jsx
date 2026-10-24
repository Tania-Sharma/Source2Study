import React, { useState, useEffect } from 'react';
import { api } from '../api';

export default function DuplicateReview({ showToast, onRefreshData }) {
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCanonical, setSelectedCanonical] = useState({}); // candidateId -> 'q1' or 'q2'
  const [customCanonicalText, setCustomCanonicalText] = useState({});

  const loadCandidates = async () => {
    setLoading(true);
    try {
      const data = await api.getDuplicateCandidates();
      setCandidates(data || []);
      // default selection to question_1
      const initialSelection = {};
      (data || []).forEach((c) => {
        initialSelection[c.id] = 'q1';
      });
      setSelectedCanonical(initialSelection);
    } catch (err) {
      showToast(`Failed to load duplicates: ${err.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCandidates();
  }, []);

  const handleMerge = async (candidate) => {
    const chosenSide = selectedCanonical[candidate.id] || 'q1';
    const canonicalObj = chosenSide === 'q1' ? candidate.question_1 : candidate.question_2;
    const duplicateObj = chosenSide === 'q1' ? candidate.question_2 : candidate.question_1;

    const chosenText = customCanonicalText[candidate.id] || canonicalObj.text;

    try {
      await api.mergeQuestions({
        canonicalId: canonicalObj.id,
        duplicateIds: [duplicateObj.id],
        chosenText: chosenText,
      });
      showToast('Questions successfully merged as duplicates!', 'success');
      setCandidates((prev) => prev.filter((c) => c.id !== candidate.id));
      onRefreshData();
    } catch (err) {
      showToast(`Merge failed: ${err.message}`, 'error');
    }
  };

  const handleMarkDistinct = async (candidate) => {
    try {
      await api.separateQuestion(candidate.question_1.id);
      await api.separateQuestion(candidate.question_2.id);
      showToast('Marked as distinct unique questions.', 'info');
      setCandidates((prev) => prev.filter((c) => c.id !== candidate.id));
      onRefreshData();
    } catch (err) {
      showToast(`Failed: ${err.message}`, 'error');
    }
  };

  return (
    <div>
      <div className="section-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1 className="section-title">
              <span>🔍</span> Duplicate Review Center
            </h1>
            <p className="section-subtitle">
              Inspect questions identified as potential duplicates across papers. Choose canonical wording, confirm merge, or mark as distinct.
            </p>
          </div>
          <button className="btn btn-secondary btn-sm" onClick={loadCandidates}>
            🔄 Refresh
          </button>
        </div>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
          Loading duplicate candidates...
        </div>
      ) : candidates.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '3rem 1rem' }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>🎉</div>
          <h3 style={{ fontSize: '1.25rem', marginBottom: '0.5rem' }}>No Pending Duplicates</h3>
          <p style={{ color: 'var(--text-secondary)', maxWidth: '450px', margin: '0 auto' }}>
            All extracted questions have been deduplicated or confirmed. Any new uncertain matches from uploaded papers will appear here.
          </p>
        </div>
      ) : (
        <div>
          <div style={{ marginBottom: '1rem', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Showing <strong>{candidates.length}</strong> candidate pair(s) requiring student verification:
          </div>

          {candidates.map((cand) => {
            const chosenSide = selectedCanonical[cand.id] || 'q1';
            return (
              <div key={cand.id} className="duplicate-group">
                {/* Header with similarity badge */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <span className={`badge ${cand.confidence === 'high' ? 'badge-exact' : 'badge-warning'}`}>
                      {Math.round(cand.similarity_score * 100)}% Similarity
                    </span>
                    <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                      Match Type: {cand.match_type.toUpperCase()}
                    </span>
                  </div>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>ID: {cand.id}</span>
                </div>

                {/* Side-by-side comparison */}
                <div className="duplicate-comparison-grid">
                  {/* Option 1 */}
                  <div
                    className="duplicate-card-side"
                    style={{
                      borderColor: chosenSide === 'q1' ? 'var(--primary)' : 'var(--border)',
                      backgroundColor: chosenSide === 'q1' ? 'rgba(59, 130, 246, 0.08)' : 'rgba(15, 23, 42, 0.5)',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                      <span className="badge badge-info">{cand.question_1.paper_name}</span>
                      <label style={{ fontSize: '0.8rem', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                        <input
                          type="radio"
                          name={`canonical_${cand.id}`}
                          checked={chosenSide === 'q1'}
                          onChange={() => setSelectedCanonical((prev) => ({ ...prev, [cand.id]: 'q1' }))}
                        />
                        Use as Canonical Wording
                      </label>
                    </div>
                    <div style={{ fontWeight: 500, fontSize: '0.95rem', color: 'var(--text-primary)', marginTop: '0.5rem' }}>
                      {cand.question_1.text}
                    </div>
                  </div>

                  {/* Option 2 */}
                  <div
                    className="duplicate-card-side"
                    style={{
                      borderColor: chosenSide === 'q2' ? 'var(--primary)' : 'var(--border)',
                      backgroundColor: chosenSide === 'q2' ? 'rgba(59, 130, 246, 0.08)' : 'rgba(15, 23, 42, 0.5)',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                      <span className="badge badge-info">{cand.question_2.paper_name}</span>
                      <label style={{ fontSize: '0.8rem', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                        <input
                          type="radio"
                          name={`canonical_${cand.id}`}
                          checked={chosenSide === 'q2'}
                          onChange={() => setSelectedCanonical((prev) => ({ ...prev, [cand.id]: 'q2' }))}
                        />
                        Use as Canonical Wording
                      </label>
                    </div>
                    <div style={{ fontWeight: 500, fontSize: '0.95rem', color: 'var(--text-primary)', marginTop: '0.5rem' }}>
                      {cand.question_2.text}
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1rem' }}>
                  <button className="btn btn-secondary btn-sm" onClick={() => handleMarkDistinct(cand)}>
                    ❌ Keep as Distinct Questions
                  </button>
                  <button className="btn btn-success btn-sm" onClick={() => handleMerge(cand)}>
                    ✓ Confirm Duplicate & Merge
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
