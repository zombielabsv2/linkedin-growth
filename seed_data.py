"""Seed the scraper database with all 69 posts from batch scrapes."""
import json
import csv
from datetime import datetime

posts = [
    {"post_text": "Google 25th Birthday - 25 years. 15 products with more than 500m daily users.", "date": "2023-09-28", "reactions": 1951, "comments": 25, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "Lightning Can Strike Twice - 10 years at Google", "date": "2023-05-21", "reactions": 1878, "comments": 102, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "IIM Ahmedabad Lessons - 10 lessons for MBA students", "date": "2022-12-10", "reactions": 1502, "comments": 100, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "What are the benefits of putting seats on top of the airplane?", "date": "2023-05-07", "reactions": 746, "comments": 38, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "Good Manager vs Nice Manager - every single day you will have a choice", "date": "2022-09-25", "reactions": 448, "comments": 35, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "Lessons from Uber Drivers - This week in the Bay Area", "date": "2022-06-08", "reactions": 428, "comments": 39, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "Career Pivot Analysis - how to determine that you should pivot", "date": "2023-10-17", "reactions": 365, "comments": 15, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "Doing a Global Role sitting out of India", "date": "2022-04-02", "reactions": 362, "comments": 17, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "Being a Noogler - wonderful opportunity to share insights", "date": "2024-03-26", "reactions": 360, "comments": 23, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "The Future of the Moat - Decision Traces", "date": "2026-01-10", "reactions": 325, "comments": 43, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "From a Bystander to An Ally - there were only 6", "date": "2024-03-12", "reactions": 300, "comments": 36, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "An impactful journey with Mr Mahindra", "date": "2024-07-13", "reactions": 297, "comments": 17, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "Stakeholder Management - a colleague sought my inputs", "date": "2022-03-24", "reactions": 243, "comments": 22, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "Mistakes I wish I had not made (Part 1)", "date": "2022-10-14", "reactions": 240, "comments": 14, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "First 90 Days as a Manager", "date": "2023-01-05", "reactions": 233, "comments": 11, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "How do I know that my partner is the right person for me?", "date": "2022-11-04", "reactions": 224, "comments": 21, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "Chandrayaan 3 / Kalpana - Imagination creates reality", "date": "2023-08-24", "reactions": 221, "comments": 13, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "Perceptions Matter - went to work in Australia", "date": "2024-04-11", "reactions": 195, "comments": 13, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "Calm Resilience - Raising the stakes for ourselves", "date": "2022-08-02", "reactions": 193, "comments": 9, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "Learned Helplessness: Quiet Quitting", "date": "2022-09-15", "reactions": 170, "comments": 21, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "Keeping the Gadfly Alive - SVB", "date": "2023-03-12", "reactions": 167, "comments": 18, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "Gap vs Gain", "date": "2022-04-13", "reactions": 166, "comments": 11, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "Every situation and every person can teach us", "date": "2022-05-25", "reactions": 165, "comments": 22, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "Your value proposition - they said change only one", "date": "2022-05-30", "reactions": 163, "comments": 6, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "Earn more. Save more. Grow more.", "date": "2023-07-15", "reactions": 163, "comments": 11, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "Winter is the time to build", "date": "2022-09-03", "reactions": 160, "comments": 8, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "Mistakes I wish I had not made (Part 2)", "date": "2022-12-24", "reactions": 155, "comments": 10, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "Where do you see yourself 10 years from now?", "date": "2022-05-07", "reactions": 153, "comments": 12, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "The five most powerful force multipliers", "date": "2022-01-18", "reactions": 151, "comments": 17, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "Say no to notifications!", "date": "2021-12-20", "reactions": 142, "comments": 14, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "Ve Haaniyaan - Where there is no love, there is no business", "date": "2024-07-27", "reactions": 138, "comments": 27, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "How should I deal with my underappreciated team member", "date": "2023-01-10", "reactions": 134, "comments": 6, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "Career Volume - Length x Breadth x Depth", "date": "2024-07-03", "reactions": 116, "comments": 10, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "Expectation mismatch to exceptional match", "date": "2022-10-01", "reactions": 114, "comments": 11, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "What these politicians wont do", "date": "2024-11-10", "reactions": 113, "comments": 17, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "What are you missing in your life? Awakening, Assets, Access", "date": "2021-08-08", "reactions": 107, "comments": 9, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "7 Wonders of AI Value - Efficiency is the floor", "date": "2025-12-24", "reactions": 105, "comments": 5, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "A source of durable inspiration: hiring people better than me", "date": "2022-06-15", "reactions": 105, "comments": 3, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "Sam is here. Being a reliable person will never go out of fashion.", "date": "2024-01-26", "reactions": 103, "comments": 12, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "We can determine to be not poor", "date": "2021-12-03", "reactions": 102, "comments": 3, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "How do I manage this person from another org?", "date": "2023-01-13", "reactions": 100, "comments": 17, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "Stakeholder Centricity IS Customer Centricity", "date": "2023-12-16", "reactions": 97, "comments": 3, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "Love will keep us alive!", "date": "2021-08-03", "reactions": 95, "comments": 6, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "Focus - do a few things really, really well", "date": "2021-10-15", "reactions": 94, "comments": 13, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "ERGs and privileges - Allama Iqbal", "date": "2021-07-30", "reactions": 92, "comments": 7, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "Never vilify a person - Randy Pausch", "date": "2024-03-02", "reactions": 88, "comments": 4, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "Love, Fragrance and Excellence", "date": "2022-10-18", "reactions": 86, "comments": 5, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "Return to Office - the return of summer is the summer of return", "date": "2022-04-06", "reactions": 84, "comments": 6, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "AI Adoption - dont chase every launch", "date": "2024-06-15", "reactions": 83, "comments": 5, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "Effort vs Impact", "date": "2022-04-22", "reactions": 83, "comments": 2, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "The three levels of victory", "date": "2022-08-31", "reactions": 81, "comments": 6, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "Are you tiring yourself out?", "date": "2021-10-22", "reactions": 79, "comments": 8, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "Action is a great distraction", "date": "2023-01-27", "reactions": 78, "comments": 5, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "WAGMI - a loss is not a loss till you book it", "date": "2022-06-10", "reactions": 77, "comments": 10, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "O-C-D: Observing. Contributing. Driving.", "date": "2024-01-08", "reactions": 76, "comments": 1, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "Coping and thriving in a largely suboptimal world", "date": "2022-08-17", "reactions": 73, "comments": 7, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "Day in the Life of a Product Manager", "date": "2022-12-29", "reactions": 71, "comments": 1, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "Youngest person in the room", "date": "2022-06-23", "reactions": 68, "comments": 4, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "How to land a transformation", "date": "2021-08-15", "reactions": 66, "comments": 8, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "Planning the battle vs battling the plan", "date": "2022-08-05", "reactions": 63, "comments": 1, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "Org Change Management - shared post", "date": "2024-06-26", "reactions": 61, "comments": 4, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "We can only give what we have", "date": "2021-12-11", "reactions": 61, "comments": 6, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "Being an ambassador - Mr Rozario", "date": "2022-09-11", "reactions": 56, "comments": 3, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "Talk and fear about slowdown / recession is a good thing", "date": "2022-06-20", "reactions": 55, "comments": 2, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "Organizational Metabolism - The Omnibus", "date": "2026-03-19", "reactions": 55, "comments": 3, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "Tomorrow is a better day", "date": "2022-12-31", "reactions": 54, "comments": 0, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "Person, Purpose and Path", "date": "2022-06-08", "reactions": 52, "comments": 9, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "Rocks, Pebbles, Sand and Water", "date": "2022-04-23", "reactions": 53, "comments": 5, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "Shadow of the Leader and Shade of the Team", "date": "2022-05-11", "reactions": 35, "comments": 3, "impressions": 0, "post_url": "", "source": "batch-scrape", "collected_at": datetime.now().isoformat()},
    {"post_text": "Aspirin at 81mg prevents heart attacks. At 500mg treats headaches.", "date": "2026-03-25", "reactions": 39, "comments": 2, "impressions": 2521, "post_url": "https://www.linkedin.com/feed/update/urn:li:share:7442620174769266688", "source": "xlsx-import", "collected_at": datetime.now().isoformat()},
]

with open("data/scraped_posts.json", "w", encoding="utf-8") as f:
    json.dump(posts, f, indent=2, ensure_ascii=False)

fields = ["post_text", "date", "reactions", "comments", "impressions", "post_url", "source", "collected_at"]
with open("data/scraped_posts.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    for p in posts:
        writer.writerow(p)

print(f"Seeded {len(posts)} posts")
