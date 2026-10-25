# LinkedIn post: final draft

Links are filled. Every number below comes from the final run (8,473 postings).
Keep the tools line that matches what you actually published (see the two options inside the post).

---

## English version

**What does it take to land a job as a Data Analyst, Product Manager or Project Manager?**

I counted instead of guessing.

I analysed 8,473 real job postings (LinkedIn, Indeed, ZipRecruiter) and measured how often each skill appears in each role.

Here are the 3 most requested skills per role:

**Data Analyst**
1. SQL: 67% of postings
2. Reporting: 67%
3. Data Visualization: 59%

**Product Manager**
1. Product Roadmap: 71%
2. Backlog / Prioritization: 65%
3. Product Strategy / Go-to-market: 55%

**Project Manager**
1. Budget Management: 56%
2. Reporting: 49%
3. Risk Management: 48%

Two things stood out:

→ SQL is about 10x more common in Data Analyst postings than in the other two roles. Python is even more role-specific (about 19x), even though only 44% of postings mention it.

→ Only 16% of Product Manager postings mention user research, but it is almost 30x more common there than in the other two roles. Rare, and it points straight at the job.

Soft skills (communication, stakeholders) appear in nearly every posting, so I listed them separately. They are expected from everyone, so they don't decide which role you fit.

How I built it:
• Python to collect, clean and classify the postings
• SQL (CTEs, window functions) to calculate demand and compare roles
• Power BI for the interactive report (project file in the repo)
• An interactive web dashboard where you pick a role and see its top 3

Limits worth knowing: postings show what employers ask for, not what people have. Skills are detected by keywords, so unusual wording can be missed. The two data sources agree closely (correlation 0.98 to 0.99).

Pick the role you want and see your top 3: https://oriyakli1-ui.github.io/linkedin-skills-analysis/
Code and method: https://github.com/oriyakli1-ui/linkedin-skills-analysis

What skill do you think is missing from the list?

#DataAnalytics #SQL #ProductManagement #ProjectManagement #CareerDevelopment #PowerBI

---

## גרסה בעברית

**מה צריך כדי להתקבל לתפקיד Data Analyst, Product Manager או Project Manager?**

במקום לנחש, ספרתי.

ניתחתי 8,473 משרות אמיתיות (לינקדאין, Indeed ו-ZipRecruiter) ובדקתי באיזה אחוז מהמשרות של כל תפקיד מופיע כל כישור.

שלושת הכישורים הנפוצים ביותר לכל תפקיד:

**Data Analyst**
1. SQL: 67% מהמשרות
2. Reporting: 67%
3. Data Visualization: 59%

**Product Manager**
1. Product Roadmap: 71%
2. Backlog / Prioritization: 65%
3. Product Strategy / Go-to-market: 55%

**Project Manager**
1. Budget Management: 56%
2. Reporting: 49%
3. Risk Management: 48%

שני דברים בלטו:

← SQL נפוץ בערך פי 10 במשרות Data Analyst לעומת שני התפקידים האחרים. Python אפילו ייחודי יותר לתפקיד (בערך פי 19), למרות שרק 44% מהמשרות מזכירות אותו.

← רק 16% ממשרות Product Manager מזכירות מחקר משתמשים (User Research), אבל הוא נפוץ שם בערך פי 30 מבשני התפקידים האחרים. כישור נדיר, והוא מצביע ישר על התפקיד.

כישורים רכים (תקשורת, ניהול בעלי עניין) מופיעים כמעט בכל משרה, ולכן הצגתי אותם בנפרד. מצפים אותם מכולם, והם לא קובעים לאיזה תפקיד אתה מתאים.

איך בניתי את זה:
• Python לאיסוף, ניקוי וסיווג המשרות
• SQL (CTE ופונקציות חלון) לחישוב ביקוש והשוואה בין התפקידים
• Power BI לדוח אינטראקטיבי (קובץ הפרויקט בריפו)
• דשבורד אינטראקטיבי באינטרנט שבו בוחרים תפקיד ורואים את שלושת הכישורים שלו

מגבלות שחשוב להכיר: משרות מראות מה מעסיקים מבקשים, לא מה יש לאנשים. זיהוי הכישורים מבוסס על מילות מפתח, ולכן ניסוחים חריגים עלולים להתפספס. שני מקורות הנתונים מסכימים ביניהם בצורה גבוהה (מתאם 0.98 עד 0.99).

בוחרים תפקיד ורואים את הטופ 3: https://oriyakli1-ui.github.io/linkedin-skills-analysis/
הקוד והמתודולוגיה: https://github.com/oriyakli1-ui/linkedin-skills-analysis

איזה כישור לדעתך חסר ברשימה?

#DataAnalytics #SQL #ProductManagement #ProjectManagement #Career
