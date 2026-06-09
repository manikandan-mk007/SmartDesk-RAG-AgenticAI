import { useState } from "react";
import { submitTicketFeedback } from "../../api/ticketApi";
import Button from "../common/Button";

export default function FeedbackModal({ ticket, onClose, onSubmitted }) {
  const [rating, setRating] = useState(4);
  const [comments, setComments] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    try {
      setLoading(true);
      await submitTicketFeedback(ticket.id, { rating, comments });
      onSubmitted();
      onClose();
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="sd-modal-backdrop">
      <div className="sd-feedback-modal">
        <h2 className="sd-feedback-title">Ticket Resolved</h2>

        <p className="sd-feedback-subtitle">
          Please share your feedback on the support experience.
        </p>

        <p className="sd-feedback-rating-label">HOW WOULD YOU RATE US?</p>

        <div className="sd-feedback-stars">
          {[1, 2, 3, 4, 5].map((star) => (
            <button
              key={star}
              type="button"
              className={`sd-feedback-star ${star <= rating ? "active" : ""}`}
              onClick={() => setRating(star)}
            >
              ★
            </button>
          ))}
        </div>

        <div className="sd-form-group sd-mt-5">
          <label className="sd-feedback-comment-label">Additional Comments</label>
          <textarea
            className="sd-feedback-textarea"
            rows="5"
            value={comments}
            onChange={(e) => setComments(e.target.value)}
            placeholder="Tell us what we can improve..."
          />
        </div>

        <Button
          className="sd-feedback-submit-btn full"
          onClick={handleSubmit}
          disabled={loading}
        >
          {loading ? "Submitting..." : "Submit Feedback"}
        </Button>

        <button
          type="button"
          className="sd-feedback-skip-btn"
          onClick={onClose}
        >
          Skip for now
        </button>
      </div>
    </div>
  );
}