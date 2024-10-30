// Create constraints to ensure uniqueness
CREATE CONSTRAINT FOR (a:Agency) REQUIRE a.name IS UNIQUE;
CREATE CONSTRAINT FOR (p:PrimeVendor) REQUIRE p.name IS UNIQUE;
CREATE CONSTRAINT FOR (b:BudgetCode) REQUIRE b.code IS UNIQUE;
CREATE CONSTRAINT FOR (c:Contract) REQUIRE c.document_id IS UNIQUE;  // Use Document ID as unique
CREATE CONSTRAINT FOR (d:Department) REQUIRE d.name IS UNIQUE;
CREATE CONSTRAINT FOR (e:ExpenseCategory) REQUIRE e.category IS UNIQUE;
CREATE CONSTRAINT FOR (pa:Payee) REQUIRE pa.name IS UNIQUE;
CREATE CONSTRAINT FOR (s:SubVendor) REQUIRE s.name IS UNIQUE;
CREATE CONSTRAINT FOR (i:Industry) REQUIRE i.name IS UNIQUE;
CREATE CONSTRAINT FOR (mw:MWBE_Category) REQUIRE mw.category IS UNIQUE;

LOAD CSV WITH HEADERS FROM 'file:///nyc_spending_feed_checks_neo_data.csv' AS row
MERGE (a:Agency {name: row.`Agency`})
MERGE (bc:BudgetCode {code: SPLIT(row.`Budget Code`, ' (')[0], description: REPLACE(SPLIT(row.`Budget Code`, ' (')[1], ')', '')})
MERGE (c:Contract {document_id: row.`Document ID`})
ON CREATE SET c.contract_id = row.`Contract ID`, 
              c.purpose = row.`Contract Purpose`, 
              c.issue_date = date(row.`Issue Date`), 
              c.fiscal_year = toInteger(row.`Fiscal year`), 
              c.check_amount = toFloat(row.`Check Amount`)
ON MATCH SET c.check_amount = c.check_amount + toFloat(row.`Check Amount`)  // Optional: Sum check amount for repeated contracts
MERGE (d:Department {name: row.`Department`})
MERGE (ec:ExpenseCategory {category: row.`Expense Category`})
MERGE (p:Payee {name: row.`Payee Name`, mwbe_category: row.`M/WBE Category`, woman_owned: row.`Woman Owned Business` = 'Yes'})
MERGE (i:Industry {name: row.`Industry`})
MERGE (sv:SubVendor {name: row.`Sub Vendor`})

// Create relationships
MERGE (a)-[:HAS_CONTRACT]->(c)
MERGE (c)-[:UNDER_BUDGET]->(bc)
MERGE (c)-[:MANAGED_BY]->(d)
MERGE (c)-[:IN_CATEGORY]->(ec)
MERGE (c)-[:PAID_TO]->(p)
MERGE (c)-[:BELONGS_TO_INDUSTRY]->(i)
MERGE (p)-[:HAS_SUBVENDOR]->(sv);
