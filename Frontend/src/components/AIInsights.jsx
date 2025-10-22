const AIInsights = ({ categories, totalDue, transactions }) => {
  const totalSpent = Object.values(categories).reduce((sum, val) => sum + (parseFloat(val) || 0), 0);
  const maxCategory = Object.entries(categories).reduce((a, b) => (parseFloat(a[1]) > parseFloat(b[1]) ? a : b))[0];
  const avgDailySpend = totalSpent / (transactions.length || 1);

  const insights = [
    `You spent the most on ${maxCategory}: ₹${categories[maxCategory].toFixed(2)}`,
    `Average daily spend: ₹${avgDailySpend.toFixed(2)}`,
    `Total due this month: ₹${totalDue} (pay at least ₹${Object.values(categories).find(cat => cat === 'minimum_amount_due') || 'N/A'})`,
    `${((totalSpent / parseFloat(totalDue)) * 100).toFixed(1)}% of your limit utilized this period.`,
  ];

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Insights</h3>
      <ul className="space-y-2 text-sm text-gray-600">
        {insights.map((insight, idx) => (
          <li key={idx} className="flex items-start">
            <svg className="w-5 h-5 text-green-500 mr-2 mt-0.5 shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            {insight}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default AIInsights;