# Plugin System Feature - Documentation Index

**Feature**: Extensible Plugin System for mcl-tool  
**Status**: 🟡 PLANNING PHASE  
**Started**: 2025-10-27  
**Target Version**: v0.3.0

---

## 📑 Documentation Structure

### Core Documents

1. **[README.md](./README..md)** - Feature Overview
   - Original feature proposal and concept
   - High-level architecture vision
   - Benefits and future possibilities
   - Example plugin ideas

2. **[architecture.md](./architecture.md)** - Technical Architecture
   - Current mcl architecture analysis
   - Proposed plugin system design
   - Integration points and flow diagrams
   - Plugin interface contract
   - Security considerations
   - Open questions and decisions

3. **[implementation-plan.md](./implementation-plan.md)** - Implementation Roadmap
   - 4 milestones with detailed tasks
   - Code examples and pseudocode
   - Time estimates (19.5h total)
   - Testing strategy
   - Risk assessment
   - Success criteria

4. **[progress-tracker.md](./progress-tracker.md)** - Live Progress Tracking
   - Task checklist with status
   - Visual progress bars
   - Blockers and issues
   - Testing status
   - Code review checklist
   - Recent activity log

5. **[ideas.md](./ideas.md)** - Future Ideas & Brainstorming
   - Enhancement ideas (hooks, aliases, sandbox)
   - Plugin ecosystem concepts
   - Technical experiments (WASM, remote)
   - Priority matrix
   - Community feedback placeholder

---

## 🎯 Quick Navigation

### For Developers Starting Implementation

1. Read [architecture.md](./architecture.md) to understand the design
2. Review [implementation-plan.md](./implementation-plan.md) for task breakdown
3. Use [progress-tracker.md](./progress-tracker.md) to track your work
4. Check [ideas.md](./ideas.md) for future considerations

### For Project Managers

- **Status**: [progress-tracker.md](./progress-tracker.md)
- **Timeline**: [implementation-plan.md](./implementation-plan.md) - Timeline section
- **Risks**: [implementation-plan.md](./implementation-plan.md) - Risk Assessment section

### For Architects/Reviewers

- **Design**: [architecture.md](./architecture.md)
- **Decisions**: [architecture.md](./architecture.md) - Open Questions section
- **Vision**: [README.md](./README..md) + [ideas.md](./ideas.md)

---

## 📊 Current Status

### Milestones Overview

| Milestone | Status | Completion | Priority |
|-----------|--------|------------|----------|
| M1: Core Infrastructure | ⬜ Not Started | 0/3 (0%) | CRITICAL |
| M2: Management Commands | ⬜ Not Started | 0/2 (0%) | HIGH |
| M3: Documentation | ⬜ Not Started | 0/3 (0%) | HIGH |
| M4: Advanced Features | ⬜ Not Started | 0/2 (0%) | MEDIUM |

**Overall Progress**: 5% (Planning Complete)

---

## 🔑 Key Decisions Made

1. **Entry Points**: Use Python's standard entry point mechanism (`mcl.plugins` namespace)
2. **Priority**: Built-in Commands > Plugins > Local Scripts > Global Scripts
3. **Context Sharing**: Environment variables (`MCL_DRY_RUN`, `MCL_SHARE_VARS`)
4. **Error Handling**: Graceful degradation - plugin failures don't crash mcl
5. **Python Compatibility**: Support 3.8+ with conditional API usage

---

## 📝 Key Architecture Points

### Plugin Discovery
- Automatic via `importlib.metadata.entry_points()`
- Namespace: `mcl.plugins`
- Cached at CLI initialization

### Command Resolution Flow
```
mcl <cmd> <args>
  ↓
1. Built-in command? → Execute
  ↓
2. Registered plugin? → Execute plugin
  ↓
3. Script in mcl.json? → Execute script
  ↓
4. Not found → Error
```

### Plugin Interface
```python
def main(args: list[str]) -> int:
    """Plugin entry point."""
    # args: Command-line arguments after plugin name
    # Returns: Exit code (0 for success)
    return 0
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- mcl-tool v0.2.0+
- Development environment setup

### Setup Development Branch
```bash
git checkout -b feature/plugin-system
```

### Install Development Dependencies
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .[dev]
```

### Run Tests
```bash
pytest tests/ -v --cov=src/mcl
```

---

## 📚 Related Documentation

- [Main Architecture](../../architecture.md)
- [API Documentation](../../api.md)
- [Development Guide](../../development.md)
- [Testing Guide](../../testing.md)

---

## 🤝 Contributing

When working on this feature:

1. **Update Progress**: Mark tasks in [progress-tracker.md](./progress-tracker.md) as you work
2. **Document Decisions**: Add to [architecture.md](./architecture.md) Open Questions section
3. **Log Activity**: Update Recent Activity in [progress-tracker.md](./progress-tracker.md)
4. **Add Ideas**: Capture future thoughts in [ideas.md](./ideas.md)
5. **Follow TDD**: Write tests before implementation

---

## 📞 Questions & Discussion

Open questions and decisions are tracked in [architecture.md](./architecture.md) - Open Questions section.

For general discussion about this feature, refer to project communication channels.

---

**Last Updated**: 2025-10-27  
**Next Review**: After M1 completion  
**Maintained By**: Development Team
