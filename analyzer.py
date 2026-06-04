import pandas as pd
import json
import os

def analyze_churn(df: pd.DataFrame, output_html="dashboard.html"):
    """Performs leak detection analysis and generates an interactive, high-end HTML dashboard."""
    print("Starting leak detection churn analysis...")
    
    # 1. Basic Churn Stats
    total_customers = len(df)
    churned_df = df[df['status'] == 'Churned']
    active_df = df[df['status'] == 'Active']
    
    total_churned = len(churned_df)
    total_active = len(active_df)
    churn_rate = (total_churned / total_customers * 100) if total_customers > 0 else 0
    
    # 2. Group Metrics (Averages)
    avg_tenure_active = active_df['tenure_days'].mean() if total_active > 0 else 0
    avg_tenure_churned = churned_df['tenure_days'].mean() if total_churned > 0 else 0
    
    avg_logins_active = active_df['login_frequency'].mean() if total_active > 0 else 0
    avg_logins_churned = churned_df['login_frequency'].mean() if total_churned > 0 else 0
    
    avg_support_active = active_df['support_contacts'].mean() if total_active > 0 else 0
    avg_support_churned = churned_df['support_contacts'].mean() if total_churned > 0 else 0
    
    avg_breaks_active = active_df['feature_breaks_encountered'].mean() if total_active > 0 else 0
    avg_breaks_churned = churned_df['feature_breaks_encountered'].mean() if total_churned > 0 else 0
    
    avg_last_login_active = active_df['days_since_last_login'].mean() if total_active > 0 else 0
    avg_last_login_churned = churned_df['days_since_last_login'].mean() if total_churned > 0 else 0

    # 3. Leak Detector Rule 1: Inactivity Leak (days_since_last_login >= 14)
    inactivity_leak_df = df[df['days_since_last_login'] >= 14]
    total_inactive = len(inactivity_leak_df)
    churned_inactive = len(inactivity_leak_df[inactivity_leak_df['status'] == 'Churned'])
    inactivity_leak_pct = (churned_inactive / total_inactive * 100) if total_inactive > 0 else 0
    
    # 4. Leak Detector Rule 2: Feature Breaks Leak (feature_breaks_encountered >= 3)
    breaks_leak_df = df[df['feature_breaks_encountered'] >= 3]
    total_breaks_users = len(breaks_leak_df)
    churned_breaks_users = len(breaks_leak_df[breaks_leak_df['status'] == 'Churned'])
    breaks_leak_pct = (churned_breaks_users / total_breaks_users * 100) if total_breaks_users > 0 else 0

    # 5. Leak Detector Rule 3: Support Contact Correlation
    support_leak_df = df[df['support_contacts'] >= 5]
    total_support_users = len(support_leak_df)
    churned_support_users = len(support_leak_df[support_leak_df['status'] == 'Churned'])
    support_leak_pct = (churned_support_users / total_support_users * 100) if total_support_users > 0 else 0

    print("Analysis results compiled.")
    print(f"Total Customers: {total_customers}")
    print(f"Churn Rate: {churn_rate:.2f}%")
    print(f"Inactivity Leak Churn Rate (>= 14 days): {inactivity_leak_pct:.2f}%")
    print(f"Feature Breaks Leak Churn Rate (>= 3 breaks): {breaks_leak_pct:.2f}%")
    print(f"Support Overhead Churn Rate (>= 5 contacts): {support_leak_pct:.2f}%")

    # Serialize customers list for dynamic table and search in HTML
    customers_list = df.to_dict(orient='records')
    
    # Render HTML content with standard TailwindCSS & glassmorphism dark theme
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Leak Detector - Customer Churn Analysis Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --border-color: rgba(255, 255, 255, 0.08);
            --accent-blue: #38bdf8;
            --accent-green: #34d399;
            --accent-red: #f87171;
            --accent-orange: #fb923c;
            --text-main: #f8fafc;
            --text-secondary: #94a3b8;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Outfit', sans-serif;
        }}

        body {{
            background-color: var(--bg-primary);
            color: var(--text-main);
            min-height: 100vh;
            padding: 2rem;
            background-image: radial-gradient(circle at 10% 20%, rgba(56, 189, 248, 0.05) 0%, transparent 40%),
                              radial-gradient(circle at 90% 80%, rgba(248, 113, 113, 0.05) 0%, transparent 40%);
            background-attachment: fixed;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        /* Header Styles */
        header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2.5rem;
            background: rgba(30, 41, 59, 0.6);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-color);
            padding: 1.5rem 2rem;
            border-radius: 1.5rem;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
        }}

        .logo-section {{
            display: flex;
            align-items: center;
            gap: 1rem;
        }}

        .logo-icon {{
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-red));
            width: 48px;
            height: 48px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-size: 1.5rem;
            color: #ffffff;
            box-shadow: 0 0 15px rgba(56, 189, 248, 0.3);
        }}

        header h1 {{
            font-size: 1.8rem;
            font-weight: 800;
            letter-spacing: -0.5px;
            background: linear-gradient(to right, #ffffff, #94a3b8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        header p {{
            font-size: 0.9rem;
            color: var(--text-secondary);
        }}

        .tutorial-btn {{
            background: linear-gradient(135deg, #ec4899, #f43f5e);
            color: white;
            text-decoration: none;
            padding: 0.8rem 1.5rem;
            border-radius: 9999px;
            font-weight: 600;
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 15px rgba(244, 63, 94, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}

        .tutorial-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(244, 63, 94, 0.4);
        }}

        /* KPI Cards Grid */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}

        .kpi-card {{
            background: rgba(30, 41, 59, 0.45);
            backdrop-filter: blur(8px);
            border: 1px solid var(--border-color);
            border-radius: 1.25rem;
            padding: 1.5rem;
            transition: transform 0.3s ease, border-color 0.3s ease;
        }}

        .kpi-card:hover {{
            transform: translateY(-2px);
            border-color: rgba(255, 255, 255, 0.15);
        }}

        .kpi-title {{
            font-size: 0.875rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 0.5rem;
        }}

        .kpi-value {{
            font-size: 2.25rem;
            font-weight: 700;
            line-height: 1.2;
            background: linear-gradient(to right, #ffffff, #cbd5e1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .kpi-trend {{
            margin-top: 0.5rem;
            font-size: 0.85rem;
            display: flex;
            align-items: center;
            gap: 0.25rem;
        }}

        .trend-up {{ color: var(--accent-red); }}
        .trend-down {{ color: var(--accent-green); }}

        /* Main Analysis Grid */
        .analysis-grid {{
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}

        @media (max-width: 1024px) {{
            .analysis-grid {{
                grid-template-columns: 1fr;
            }}
        }}

        .dashboard-box {{
            background: rgba(30, 41, 59, 0.45);
            backdrop-filter: blur(8px);
            border: 1px solid var(--border-color);
            border-radius: 1.5rem;
            padding: 2rem;
        }}

        .box-title {{
            font-size: 1.25rem;
            font-weight: 700;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}

        /* Leak Cards */
        .leak-list {{
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }}

        .leak-card {{
            background: rgba(15, 23, 42, 0.5);
            border-radius: 1rem;
            border: 1px solid var(--border-color);
            padding: 1.25rem;
            display: flex;
            align-items: flex-start;
            gap: 1rem;
            transition: all 0.3s ease;
        }}

        .leak-card:hover {{
            background: rgba(15, 23, 42, 0.8);
            border-color: rgba(255, 255, 255, 0.12);
        }}

        .leak-icon {{
            background: rgba(248, 113, 113, 0.1);
            color: var(--accent-red);
            padding: 0.75rem;
            border-radius: 0.75rem;
            font-weight: 800;
            font-size: 1.2rem;
            line-height: 1;
        }}

        .leak-info {{
            flex-grow: 1;
        }}

        .leak-info h3 {{
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 0.25rem;
        }}

        .leak-info p {{
            font-size: 0.875rem;
            color: var(--text-secondary);
            margin-bottom: 0.5rem;
        }}

        .leak-badge {{
            display: inline-block;
            padding: 0.25rem 0.6rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            background: rgba(248, 113, 113, 0.15);
            color: var(--accent-red);
            border: 1px solid rgba(248, 113, 113, 0.25);
        }}

        /* Table & Directory Styles */
        .directory-section {{
            margin-bottom: 2rem;
        }}

        .filters-bar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
            margin-bottom: 1.5rem;
            flex-wrap: wrap;
        }}

        .search-input {{
            background: rgba(15, 23, 42, 0.5);
            border: 1px solid var(--border-color);
            color: white;
            padding: 0.75rem 1.25rem;
            border-radius: 0.75rem;
            font-size: 0.9rem;
            min-width: 300px;
            outline: none;
            transition: border-color 0.3s ease;
        }}

        .search-input:focus {{
            border-color: var(--accent-blue);
        }}

        .filter-buttons {{
            display: flex;
            gap: 0.5rem;
        }}

        .filter-btn {{
            background: rgba(15, 23, 42, 0.5);
            border: 1px solid var(--border-color);
            color: var(--text-secondary);
            padding: 0.6rem 1.2rem;
            border-radius: 0.75rem;
            font-size: 0.875rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }}

        .filter-btn.active, .filter-btn:hover {{
            background: var(--accent-blue);
            color: #0f172a;
            border-color: var(--accent-blue);
        }}

        .table-container {{
            overflow-x: auto;
            border-radius: 1rem;
            border: 1px solid var(--border-color);
            background: rgba(30, 41, 59, 0.2);
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 0.9rem;
        }}

        th, td {{
            padding: 1rem 1.5rem;
            border-bottom: 1px solid var(--border-color);
        }}

        th {{
            background: rgba(15, 23, 42, 0.4);
            font-weight: 600;
            color: var(--text-secondary);
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 0.5px;
        }}

        tr:hover {{
            background: rgba(255, 255, 255, 0.02);
        }}

        .status-badge {{
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 0.375rem;
            font-size: 0.75rem;
            font-weight: 600;
        }}

        .status-active {{
            background: rgba(52, 211, 153, 0.15);
            color: var(--accent-green);
        }}

        .status-churned {{
            background: rgba(248, 113, 113, 0.15);
            color: var(--accent-red);
        }}

        .risk-badge {{
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 0.375rem;
            font-size: 0.75rem;
            font-weight: 600;
        }}

        .risk-high {{
            background: rgba(248, 113, 113, 0.15);
            color: var(--accent-red);
        }}

        .risk-medium {{
            background: rgba(251, 146, 60, 0.15);
            color: var(--accent-orange);
        }}

        .risk-low {{
            background: rgba(52, 211, 153, 0.15);
            color: var(--accent-green);
        }}

        /* Recommendations Section */
        .recs-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}

        .rec-card {{
            background: rgba(30, 41, 59, 0.45);
            backdrop-filter: blur(8px);
            border: 1px solid var(--border-color);
            border-radius: 1.25rem;
            padding: 1.5rem;
            transition: all 0.3s ease;
        }}

        .rec-card:hover {{
            transform: translateY(-2px);
            border-color: var(--accent-blue);
        }}

        .rec-header {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 1rem;
        }}

        .rec-icon {{
            font-size: 1.5rem;
        }}

        .rec-card h4 {{
            font-size: 1.1rem;
            font-weight: 700;
        }}

        .rec-card p {{
            font-size: 0.9rem;
            color: var(--text-secondary);
            line-height: 1.5;
            margin-bottom: 1rem;
        }}

        .rec-checklist {{
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }}

        .rec-checklist li {{
            font-size: 0.85rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: var(--text-main);
        }}

        .checkbox-bullet {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--accent-blue);
        }}

        /* Chart Canvas Size Control */
        .chart-container {{
            position: relative;
            height: 300px;
            width: 100%;
            margin-top: 1rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <header>
            <div class="logo-section">
                <div class="logo-icon">🔍</div>
                <div>
                    <h1>The Leak Detector</h1>
                    <p>Customer Churn Analysis Pipeline Dashboard</p>
                </div>
            </div>
            <a href="https://www.youtube.com/watch?v=dQw4w9WgXcQ" target="_blank" class="tutorial-btn">
                <span>📹</span> Watch Tutorial
            </a>
        </header>

        <!-- KPI Grid -->
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">Total Customers</div>
                <div class="kpi-value">{total_customers}</div>
                <div class="kpi-trend trend-down">Active: {total_active} | Churned: {total_churned}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Average Churn Rate</div>
                <div class="kpi-value">{churn_rate:.1f}%</div>
                <div class="kpi-trend trend-up">⚠️ High leakage detected</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Inactivity Churn Risk</div>
                <div class="kpi-value">{inactivity_leak_pct:.1f}%</div>
                <div class="kpi-trend trend-up">If unlogged for &ge; 14 days</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Feature Break Impact</div>
                <div class="kpi-value">{breaks_leak_pct:.1f}%</div>
                <div class="kpi-trend trend-up">If encounters &ge; 3 breaks</div>
            </div>
        </div>

        <!-- Main Charts & Leak Detector Panel -->
        <div class="analysis-grid">
            <!-- Left Side: Interactive Charts -->
            <div class="dashboard-box">
                <div class="box-title">
                    <span>Behavioral Churn Drivers</span>
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 2rem;">
                    <div>
                        <h4 style="text-align: center; font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 0.5rem;">Customer Status Breakdown</h4>
                        <div class="chart-container">
                            <canvas id="churnPieChart"></canvas>
                        </div>
                    </div>
                    <div>
                        <h4 style="text-align: center; font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 0.5rem;">Customer Health Metrics Comparison</h4>
                        <div class="chart-container">
                            <canvas id="metricsBarChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Right Side: Leak Detector Panel -->
            <div class="dashboard-box">
                <div class="box-title">
                    <span>Active Leaks Detected</span>
                    <span style="font-size: 0.8rem; padding: 0.2rem 0.5rem; border-radius: 9999px; background: rgba(248, 113, 113, 0.2); color: var(--accent-red);">Critical</span>
                </div>
                <div class="leak-list">
                    <!-- Leak 1 -->
                    <div class="leak-card">
                        <div class="leak-icon">🔌</div>
                        <div class="leak-info">
                            <h3>Specific Feature Breaks</h3>
                            <p>Users encountering bugs are highly prone to immediate cancellations.</p>
                            <span class="leak-badge">Churn Rate: {breaks_leak_pct:.1f}%</span>
                        </div>
                    </div>
                    <!-- Leak 2 -->
                    <div class="leak-card">
                        <div class="leak-icon">💤</div>
                        <div class="leak-info">
                            <h3>Inactivity &gt; 14 Days</h3>
                            <p>Failure to log in within two weeks leads directly to subscription cancellations.</p>
                            <span class="leak-badge">Churn Rate: {inactivity_leak_pct:.1f}%</span>
                        </div>
                    </div>
                    <!-- Leak 3 -->
                    <div class="leak-card">
                        <div class="leak-icon">🛠️</div>
                        <div class="leak-info">
                            <h3>High Support Tickets</h3>
                            <p>Customers with frequent support contacts churn due to recurring frustrations.</p>
                            <span class="leak-badge">Churn Rate: {support_leak_pct:.1f}%</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Retention Strategy Section -->
        <div class="dashboard-box" style="margin-bottom: 2rem;">
            <div class="box-title">Actionable Retention Strategy Plan</div>
            <div class="recs-grid">
                <div class="rec-card">
                    <div class="rec-header">
                        <span class="rec-icon">⚡</span>
                        <h4>1. Feature Bug Fixes</h4>
                    </div>
                    <p>Address software bugs and friction areas where specific features break, as they cause immediate subscription churn.</p>
                    <ul class="rec-checklist">
                        <li><span class="checkbox-bullet"></span> Set up automated alerts for core API errors</li>
                        <li><span class="checkbox-bullet"></span> Prioritize bug tickets for high-value accounts</li>
                    </ul>
                </div>
                <div class="rec-card">
                    <div class="rec-header">
                        <span class="rec-icon">📬</span>
                        <h4>2. Re-engagement Campaigns</h4>
                    </div>
                    <p>Launch targeted email and notification sequences when days since last login reaches 7 days to prevent the 14-day inactivity cliff.</p>
                    <ul class="rec-checklist">
                        <li><span class="checkbox-bullet"></span> Set automated reminder emails at day 7</li>
                        <li><span class="checkbox-bullet"></span> Offer value tips / tutorial recap video</li>
                    </ul>
                </div>
                <div class="rec-card">
                    <div class="rec-header">
                        <span class="rec-icon">🤝</span>
                        <h4>3. Proactive Customer Success</h4>
                    </div>
                    <p>Flag and contact customers who file more than 4 support tickets within a single month to address concerns before they choose to cancel.</p>
                    <ul class="rec-checklist">
                        <li><span class="checkbox-bullet"></span> Flag users with high support contacts</li>
                        <li><span class="checkbox-bullet"></span> Implement custom check-in calls</li>
                    </ul>
                </div>
            </div>
        </div>

        <!-- Customer Directory -->
        <div class="dashboard-box directory-section">
            <div class="box-title">
                <span>Customer Database & Directory</span>
            </div>
            
            <div class="filters-bar">
                <input type="text" id="searchInput" class="search-input" placeholder="Search by name, email...">
                
                <div class="filter-buttons">
                    <button class="filter-btn active" onclick="filterStatus('All')">All</button>
                    <button class="filter-btn" onclick="filterStatus('Active')">Active</button>
                    <button class="filter-btn" onclick="filterStatus('Churned')">Churned</button>
                </div>
            </div>

            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Email</th>
                            <th>Tenure (Days)</th>
                            <th>Login Frequency (Mo)</th>
                            <th>Support Tickets</th>
                            <th>Feature Breaks</th>
                            <th>Days Since Last Login</th>
                            <th>Risk Level</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody id="customerTableBody">
                        <!-- Filled by JS -->
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        // Injected data from python process
        const customers = {json.dumps(customers_list)};

        function calculateRiskLevel(customer) {{
            if (customer.days_since_last_login >= 10 || customer.feature_breaks_encountered >= 3 || customer.support_contacts >= 8) {{
                return 'High';
            }} else if (customer.days_since_last_login >= 7 || customer.feature_breaks_encountered >= 2 || customer.support_contacts >= 4) {{
                return 'Medium';
            }} else {{
                return 'Low';
            }}
        }}

        let currentStatusFilter = 'All';

        function renderTable() {{
            const searchVal = document.getElementById('searchInput').value.toLowerCase();
            const tbody = document.getElementById('customerTableBody');
            tbody.innerHTML = '';
            
            const filtered = customers.filter(c => {{
                const matchesSearch = c.name.toLowerCase().includes(searchVal) || c.email.toLowerCase().includes(searchVal);
                const matchesStatus = currentStatusFilter === 'All' || c.status === currentStatusFilter;
                return matchesSearch && matchesStatus;
            }});

            filtered.forEach(c => {{
                const tr = document.createElement('tr');
                const risk = calculateRiskLevel(c);
                
                let riskClass = 'risk-low';
                if (risk === 'High') riskClass = 'risk-high';
                else if (risk === 'Medium') riskClass = 'risk-medium';

                const statusClass = c.status === 'Active' ? 'status-active' : 'status-churned';

                tr.innerHTML = `
                    <td style="font-weight: 600;">${{c.id}}</td>
                    <td>${{c.name}}</td>
                    <td style="color: var(--text-secondary); font-size: 0.85rem;">${{c.email}}</td>
                    <td>${{c.tenure_days}}</td>
                    <td>${{c.login_frequency}}</td>
                    <td>${{c.support_contacts}}</td>
                    <td>${{c.feature_breaks_encountered}}</td>
                    <td>${{c.days_since_last_login}}</td>
                    <td><span class="risk-badge ${{riskClass}}">${{risk}}</span></td>
                    <td><span class="status-badge ${{statusClass}}">${{c.status}}</span></td>
                `;
                tbody.appendChild(tr);
            }});
        }}

        function filterStatus(status) {{
            currentStatusFilter = status;
            
            // Update button states
            document.querySelectorAll('.filter-btn').forEach(btn => {{
                if (btn.innerText === status || (status === 'All' && btn.innerText === 'All')) {{
                    btn.classList.add('active');
                }} else {{
                    btn.classList.remove('active');
                }}
            }});

            renderTable();
        }}

        document.getElementById('searchInput').addEventListener('input', renderTable);

        // Initial setup
        renderTable();

        // Setup Charts
        const activeCount = {total_active};
        const churnedCount = {total_churned};

        // Pie Chart
        new Chart(document.getElementById('churnPieChart'), {{
            type: 'doughnut',
            data: {{
                labels: ['Active', 'Churned'],
                datasets: [{{
                    data: [activeCount, churnedCount],
                    backgroundColor: ['#34d399', '#f87171'],
                    borderColor: '#1e293b',
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'bottom',
                        labels: {{
                            color: '#94a3b8',
                            font: {{ family: 'Outfit', size: 12 }}
                        }}
                    }}
                }}
            }}
        }});

        // Bar Chart
        new Chart(document.getElementById('metricsBarChart'), {{
            type: 'bar',
            data: {{
                labels: ['Logins', 'Support Tickets', 'Bugs Encountered', 'Inactivity (Days)'],
                datasets: [
                    {{
                        label: 'Active Customers',
                        data: [{avg_logins_active:.2f}, {avg_support_active:.2f}, {avg_breaks_active:.2f}, {avg_last_login_active:.2f}],
                        backgroundColor: '#34d399',
                        borderRadius: 6
                    }},
                    {{
                        label: 'Churned Customers',
                        data: [{avg_logins_churned:.2f}, {avg_support_churned:.2f}, {avg_breaks_churned:.2f}, {avg_last_login_churned:.2f}],
                        backgroundColor: '#f87171',
                        borderRadius: 6
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'bottom',
                        labels: {{
                            color: '#94a3b8',
                            font: {{ family: 'Outfit', size: 12 }}
                        }}
                    }}
                }},
                scales: {{
                    x: {{
                        ticks: {{ color: '#94a3b8', font: {{ family: 'Outfit' }} }},
                        grid: {{ display: false }}
                    }},
                    y: {{
                        ticks: {{ color: '#94a3b8', font: {{ family: 'Outfit' }} }},
                        grid: {{ color: 'rgba(255, 255, 255, 0.05)' }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""

    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    print(f"Interactive dashboard generated successfully at: {os.path.abspath(output_html)}")

if __name__ == "__main__":
    # Test script
    import os
    if os.path.exists("cleaned_data.csv"):
        cleaned_df = pd.read_csv("cleaned_data.csv")
        analyze_churn(cleaned_df)
