# Core Invariants

Use the lifecycle `Problem -> Authority -> Contract -> Evidence -> Plan -> Code -> Gate -> Release -> Feedback -> Problem`.

Never delete these questions:
1. Is the problem correct?
2. Is the authority/contract explicit?
3. What evidence proves the result?
4. Who or what Gate decides whether downstream work may proceed?

Route to the earliest untrusted layer. `Code Complete != Gate Complete`. Do not silently change upstream authority to make downstream work easier.
