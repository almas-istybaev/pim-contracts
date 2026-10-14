---
description: "Strict boundary constraints preventing AI from modifying external projects"
---
# STRICT BOUNDARY RULES

1. **NEVER** navigate, read, or modify files outside of the current workspace directory.
2. **DO NOT** attempt to automatically update or edit other projects, microservices, or repositories, even if they are closely related or are dependencies of the current project (e.g., do not edit `price-list-processor` when working inside `pim-contracts`, and vice versa).
3. Если задача требует изменений во внешнем проекте, **ОСТАНОВИТЕСЬ** и сообщите пользователю, что он должен внести эти изменения самостоятельно или открыть другой проект.
4. **ЭТО СТРОГОЕ, НЕОБСУЖДАЕМОЕ ПРАВИЛО.** Нарушение границ проекта категорически запрещено.
