import { PieChart, Pie, Cell, ResponsiveContainer, Legend } from "recharts";

const SpendingInsights = ({ categories }) => {
  const data = Object.entries(categories)
    .map(([name, value]) => ({
      name,
      value: parseFloat(value) || 0,
    }))
    .filter((item) => item.value > 0);

  const COLORS = [
    "#FF6B6B",
    "#4ECDC4",
    "#45B7D1",
    "#96CEB4",
    "#FFEEAD",
    "#D4A5A5",
    "#9B59B6",
  ];

  const total = data.reduce((sum, entry) => sum + entry.value, 0);

  return (
    <div className="bg-white shadow rounded-xl p-4 sm:p-5 md:p-6">
      <h3 className="text-lg sm:text-xl font-semibold text-gray-900 mb-4 sm:mb-6">
        Spending by Category
      </h3>

      {data.length > 0 ? (
        <>
          {/* Responsive Chart Container */}
          <div className="w-full h-56 sm:h-64 md:h-72 lg:h-80">
            <ResponsiveContainer>
              <PieChart>
                <Pie
                  data={data}
                  cx="50%"
                  cy="50%"
                  innerRadius="45%"
                  outerRadius="70%"
                  dataKey="value"
                  labelLine={false}
                  label={({ name, value, cx, cy, midAngle, outerRadius }) => {
                    const RADIAN = Math.PI / 180;
                    const radius = outerRadius * 1.15;
                    const x = cx + radius * Math.cos(-midAngle * RADIAN);
                    const y = cy + radius * Math.sin(-midAngle * RADIAN);
                    const percentage = ((value / total) * 100).toFixed(1);
                    return (
                      <text
                        x={x}
                        y={y}
                        fill="#333"
                        textAnchor={x > cx ? "start" : "end"}
                        dominantBaseline="central"
                        className="text-[10px] sm:text-xs md:text-sm font-medium"
                      >
                        {`${name} (${percentage}%)`}
                      </text>
                    );
                  }}
                >
                  {data.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={COLORS[index % COLORS.length]}
                    />
                  ))}
                </Pie>

                <Legend
                  layout="horizontal"
                  verticalAlign="bottom"
                  align="center"
                  iconType="circle"
                  wrapperStyle={{
                    paddingTop: "16px",
                    fontSize: "0.85rem",
                  }}
                  formatter={(value) => (
                    <span className="text-gray-700 font-medium">{value}</span>
                  )}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Bottom List with Perfect Spacing */}
          <div className="mt-6 grid grid-cols-1 sm:grid-cols-1 md:grid-cols-1 lg:grid-cols-1 gap-3 sm:gap-4">
            {data.map((entry, idx) => (
              <div
                key={entry.name}
                className="flex items-center justify-between bg-gray-50 rounded-lg px-3 py-2 sm:px-4 sm:py-3 shadow-sm hover:bg-gray-100 transition-all duration-200"
              >
                <div className="flex items-center space-x-2">
                  <div
                    className="w-3 h-3 sm:w-4 sm:h-4 rounded-full"
                    style={{ backgroundColor: COLORS[idx % COLORS.length] }}
                  ></div>
                  <span className="text-gray-700 text-sm sm:text-base font-medium truncate">
                    {entry.name}
                  </span>
                </div>
                <span className="font-semibold text-gray-900 text-sm sm:text-base">
                  ₹{entry.value.toFixed(2)}
                </span>
              </div>
            ))}
          </div>
        </>
      ) : (
        <p className="text-center text-gray-500 text-sm sm:text-base md:text-lg">
          No spending data available.
        </p>
      )}
    </div>
  );
};

export default SpendingInsights;
