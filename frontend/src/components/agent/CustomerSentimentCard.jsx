function polarToCartesian(cx, cy, r, angle) {
  const radians = ((angle - 180) * Math.PI) / 180.0;
  return {
    x: cx + r * Math.cos(radians),
    y: cy + r * Math.sin(radians),
  };
}

function describeArc(cx, cy, r, startAngle, endAngle) {
  const start = polarToCartesian(cx, cy, r, endAngle);
  const end = polarToCartesian(cx, cy, r, startAngle);
  const largeArcFlag = endAngle - startAngle <= 180 ? "0" : "1";

  return [
    "M", start.x, start.y,
    "A", r, r, 0, largeArcFlag, 0, end.x, end.y,
  ].join(" ");
}

function classifySentimentCounts(data = []) {
  let positive = 0;
  let negative = 0;
  let neutral = 0;

  data.forEach((item) => {
    const label = String(item.label).toUpperCase();
    const count = item.count || 0;

    if (["POSITIVE", "CALM"].includes(label)) positive += count;
    else if (["ANGRY", "FRUSTRATED", "URGENT"].includes(label)) negative += count;
    else neutral += count;
  });

  return { positive, negative, neutral };
}

export default function CustomerSentimentCard({ data = [] }) {
  const { positive, negative, neutral } = classifySentimentCounts(data);
  const total = positive + negative + neutral || 1;

  const positivePercent = Math.round((positive / total) * 100);
  const angle = 180 - (positivePercent / 100) * 180;

  const score = (5 + (positivePercent / 20)).toFixed(1);
  const status =
    positivePercent >= 60 ? "Positive" : positivePercent >= 35 ? "Neutral" : "Negative";

  return (
    <div className="sd-card pad sd-dashboard-small-card">
      <h3 className="sd-heading-sm">Customer Sentiment</h3>

      <div className="sd-sentiment-gauge-wrap">
        <svg viewBox="0 0 160 100" className="sd-sentiment-gauge-svg">
          <path
            d={describeArc(80, 80, 52, 180, 0)}
            fill="none"
            stroke="#e8e8e8"
            strokeWidth="12"
            strokeLinecap="round"
          />
          <path
            d={describeArc(80, 80, 52, 180, angle)}
            fill="none"
            stroke="#000000"
            strokeWidth="12"
            strokeLinecap="round"
          />
        </svg>

        <div className="sd-sentiment-status">{status}</div>
        <p className="sd-body sd-muted sd-center sd-mt-2">
          Sentiment is based on current ticket distribution.
        </p>
      </div>

      <div className="sd-sentiment-stats">
        <div>
          <div className="sd-sentiment-stat-value">{score}</div>
          <div className="sd-sentiment-stat-label">Avg Score</div>
        </div>
        <div>
          <div className="sd-sentiment-stat-value">{negative}</div>
          <div className="sd-sentiment-stat-label">Negative</div>
        </div>
        <div>
          <div className="sd-sentiment-stat-value">{positive}</div>
          <div className="sd-sentiment-stat-label">Positive</div>
        </div>
      </div>
    </div>
  );
}