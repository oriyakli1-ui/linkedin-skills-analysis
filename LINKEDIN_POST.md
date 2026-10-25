# LinkedIn post: final draft (English)

Attach: `carousel/carousel.pdf` (Add a document). Every number comes from the final run (8,473 postings).
Tip: LinkedIn shows only the first ~3 lines before "see more", so the opening carries the post.

---

I'm an Industrial Engineering & Management student, and three roles keep coming up in every conversation about jobs on campus: Product Manager, Project Manager and Data Analyst.

So I asked a simple question: what do employers actually ask for in these three roles?

Instead of guessing, I counted. I analysed 8,473 real job postings (LinkedIn, Indeed, ZipRecruiter) and measured how often each skill shows up.

The top 3 per role:

📊 Data Analyst
1. SQL (67% of postings)
2. Reporting (67%)
3. Data Visualization (59%)

🧭 Product Manager
1. Product Roadmap (71%)
2. Backlog / Prioritization (65%)
3. Product Strategy / Go-to-market (55%)

🗂️ Project Manager
1. Budget Management (56%)
2. Reporting (49%)
3. Risk Management (48%)

Two things surprised me:

→ SQL appears about 10x more often in Data Analyst postings than in the other two roles. It's not just popular, it defines the job.

→ Communication is in 69-85% of postings in every role. Everyone expects it, so it won't set you apart. The hard skills will.

I built the whole thing myself: Python to collect and clean the postings, SQL to calculate demand (CTEs and window functions), and Power BI plus a small web dashboard so you can pick a role and see its top 3.

A fair warning: postings show what employers ask for, not what people actually have, and I detect skills by keywords, so unusual wording can slip through. The two data sources agree closely, though (correlation 0.98-0.99).

And a tip for friends looking for a job in these fields: pick your role, learn the top skills on its list, and add them to your LinkedIn profile. I already did, and it made it much clearer to me what I'm aiming for.

Pick your role and see your top 3: https://oriyakli1-ui.github.io/linkedin-skills-analysis/
Code and method: https://github.com/oriyakli1-ui/linkedin-skills-analysis

Which skill do you think is missing from the list? 👇

#IndustrialEngineering #DataAnalytics #SQL #ProductManagement #ProjectManagement #PowerBI #Students
