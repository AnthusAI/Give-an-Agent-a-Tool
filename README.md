# Give an Agent a Tool: A Programming Paradigm Shift

> *"If you give an agent a tool, then nobody has to fish."*

## From Code Complexity to Intelligent Delegation

For decades, learning to write computer code has been one of the most challenging skills a person could master. Programming meant thinking like a machine—anticipating every possible scenario, handling every edge case, and writing explicit instructions for each step. It was a uniquely human burden: translating complex real-world problems into rigid, logical sequences that computers could follow.

Here’s the real-world story we’re solving:

We receive people data from many places (CRM exports, event sign-ups, HR spreadsheets, legacy systems). Each file is a table, but headers, orders, and languages vary. The simple business goal is the same every time: **extract each person’s name and email**.

Some examples you might see on the same day:

Common CRM export

| First Name | Last Name | Email            |
|------------|-----------|------------------|
| John       | Doe       | john@example.com |
| Jane       | Smith     | jane@test.org    |

Last, First ordering

| Last | First | Email            |
|------|-------|------------------|
| Doe  | John  | john@example.com |
| Smith| Jane  | jane@test.org    |

Different header names + extra columns

| NAME        | WORK EMAIL         | ID   |
|-------------|--------------------|------|
| John Doe    | john@example.com   | 101  |
| Jane Smith  | jane@test.org      | 102  |

Phone present, email renamed

| Name       | Company | Primary Email      | Phone         |
|------------|---------|--------------------|---------------|
| John Doe   | Acme    | john@example.com   | 555-123-4567  |
| Jane Smith | TechInc | jane@test.org      | 555-987-6543  |

International (Spanish)

| Nombre | Apellidos | Correo            |
|--------|-----------|-------------------|
| Luis   | García    | luis@empresa.es   |
| María  | López     | maria@test.es     |

Shouted headers, different order

| EMAIL            | NAME        |
|------------------|-------------|
| john@example.com | John Doe    |
| jane@test.org    | Jane Smith  |

We wrote traditional, explicit code to handle those cases with lots of if/else:

- Map header synonyms (First/Given/Nombre → first_name; Email/Work Email/Correo → email)
- Detect column order (First/Last vs Last/First vs single Name)
- Handle extra columns (ID, Company, Phone) and pick the right ones

 

### How we’d implement this traditionally

Pseudocode:

```text
synonyms = {
  first_name: [first, "first name", given, nombre],
  last_name:  [last, "last name", surname, apellidos],
  email:      [email, "work email", correo, "email address"]
}

table = parse_table(text, auto_detect_delimiter = true)
headers = normalize_headers(table.headers, using = synonyms)

out = []
for each row in table.rows:
  (first, last) = infer_name(row, headers)
    - if name == "Last, First" -> split on comma
    - else if single NAME -> split on space(s)
  email = find_email(row, headers, fallback_to_notes = true)
  if missing(first) and missing(last) or missing(email):
    error "Missing name or email — add another case"
  out.append({first_name: first, last_name: last, email: email})

return out

# …plus delimiter detection, header detection, phone parsing branches, locale rules, etc.
```

…and then this arrives:

Unexpected legacy export (mixed fields)

| Contact Info          | Details                                        |
|-----------------------|-----------------------------------------------|
| "Smith, Jane (Mgr)"  | "jane.smith@company.com | Mobile: +1-555-0123" |
| "Rodriguez, Carlos"  | "carlos.r@email.com Phone: 555.987.6543"      |

> ❌ Error
>
> ```text
> ValueError: Unsupported headers: Contact Info, Details
> Hint: No mapping for 'Contact Info'. Expected one of: first, last, name, email, correo, …
> ```
>
> We didn’t anticipate this header scheme or the mixed email/phone cell. The import fails.

This works until a new variation appears (like the legacy export above), at which point we add more mappings and conditionals.

## The New Way: Intelligent Agents with Tools

Today, instead of anticipating every scenario, we provide a single capability and a goal to an intelligent agent. The agent decides everything else. Now that the limits of hard-coded logic are clear, here’s how the agent approach works.

### How the agent-based approach works

Instead of growing a thicket of if/else, we give one business action to an agent and describe the goal:

- file_contact(name, email?, phone?): store a single contact (requires name and one of email or phone)

When the unexpected legacy export arrives, the agent “thinks” in steps: “Read the table that follows, infer headers if any, find each person’s name and either an email or phone, and call file_contact for each.” We didn’t add new branches; we simply provided the filing action.

Agent prompt:

```text
You are a contact import assistant.
Goal: read the CSV below and file each contact you can find.
Use the single tool file_contact(name, email?, phone?) to file each person.
Infer names and emails/phones from whatever headers or content appear.
```

Tool stub:

```text
tool file_contact(name, email?, phone?):
  save a single contact record where name is required
  and at least one of email or phone is provided
```



The key difference: when a new variation appears, we don’t patch conditionals—we reuse the same tools, and the agent adapts how it sequences them.

This is the burden programmers have carried with traditional code: **you must think of everything**. Every header synonym (First vs Given vs Nombre), every column order, every language, every messy field. Miss one scenario, and your program breaks.

 

## Why This Matters for Everyone

You don't need to be a programmer to understand why this is revolutionary:

- **Traditional programming**: Like writing a 500-page manual for every possible situation an employee might encounter
- **Agent programming**: Like hiring a smart employee, giving them the right tools, and trusting them to figure it out

The first approach requires you to think of everything. The second approach lets intelligence emerge from the combination of simple tools and smart delegation.

This project demonstrates this paradigm shift using a classic computer science problem that any programmer would recognize—but solved in both the old way and the new way. You'll see how the same task that requires hundreds of lines of complex branching logic in traditional programming becomes simple and flexible with an agent approach.

## “In the future, the only code you will write is business logic.”
_— Werner Vogels, CTO of AWS_

This example is exactly that. We don’t enumerate formats—we implement the one capability the business cares about and let the agent do the rest. In our story, that capability is the single tool `file_contact(name, email?, phone?)`.

Writing code is not the hard part. The hard part is keeping code working over time as inputs change and people depend on it. What really drives time and money over the long run:
- Changes keep coming: vendor export tweaks, new languages, new columns
- Every new rule risks breaking something else
- Time spent coordinating changes across teams
- Outages: failed imports can interrupt the business
- Duplicate logic spreads and drifts across systems

With agents, that long‑term cost shifts from “rewrite rules for each new case” to “reuse the same tool and let the agent adapt.” You maintain far less code and lower the chance of interruptions, while keeping the only code you write—the business tool—simple and focused.

 

 

## Handling Unexpected Formats: The Real Test

The true power of the agent approach becomes clear when encountering **completely unexpected data formats** that weren't anticipated during development.

### Example: Messy Real-World Export

Imagine receiving this CSV from a legacy system:
```csv
"Contact Info","Details","Extra"
"Smith, Jane (Manager)","jane.smith@company.com | Mobile: +1-555-0123","Dept: Sales, Start: 2020"
"Rodriguez, Carlos","carlos.r@email.com Phone: 555.987.6543","Engineering Team Lead"
```

**Traditional Approach Result:**
- ❌ Breaks completely - doesn't recognize the format
- ❌ Can't parse names with titles in parentheses
- ❌ Can't extract emails/phones from mixed delimiter fields
- ❌ Would require major code changes to handle this format

**Agent Approach Result:**
- ✅ Automatically recognizes it's CSV despite unusual structure
- ✅ Intelligently parses "Smith, Jane (Manager)" → First: Jane, Last: Smith
- ✅ Extracts email and phone from mixed delimiter strings
- ✅ Handles it with the same tools, no code changes needed

This demonstrates **true agility** - the ability to handle evolving requirements and unexpected data without rewriting core logic.

## Inspired By

This project was inspired by [SQLBot](https://github.com/AnthusAI/SQLBot), which demonstrates this paradigm shift in the context of database querying. SQLBot shows how an agent with SQL tools can be more flexible than traditional query builders.

## Run It Yourself

### Setup

```bash
git clone <this-repo>
cd Give-an-Agent-a-Tool
pip install -r requirements.txt
```

### Configure OpenAI

```bash
cp env.example .env
# Edit .env and add your OpenAI API key
```

### Run the Traditional Approach

```bash
python traditional_approach.py
```

### Run the Agent Approach

```bash
python agent_approach.py
```

### Run Tests

```bash
pytest tests/ -v
```

---

*"Give a man a fish and you feed him for a day. Teach a man to fish and you feed him for a lifetime. Give an agent a tool and nobody has to fish."*
