"""Main entry point for the self-building LangChain system."""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from core import build_loop, state_manager
from agents.orchestrator import orchestrator


async def main():
    """Main entry point."""
    print("=" * 60)
    print("Self-Building LangChain System")
    print("=" * 60)
    
    # Load existing state
    print("\nLoading system state...")
    state = await state_manager.load()
    print(f"State loaded: {len(state.capabilities)} capabilities, {len(state.generated_files)} files")
    
    # Run the self-build loop and monitor/improve loop concurrently
    print("\nStarting self-build loop and monitoring loop...\n")
    await asyncio.gather(
        build_loop.run(),
        orchestrator.monitor_and_improve(interval_seconds=600)
    )
    
    print("\n" + "=" * 60)
    print("Self-build process complete!")
    print("=" * 60)
    
    # Print summary
    final_state = await state_manager.get_state()
    print(f"\nFinal state:")
    print(f"  - Total capabilities: {len(final_state.capabilities)}")
    print(f"  - Implemented: {sum(1 for c in final_state.capabilities if c.implemented)}")
    print(f"  - Generated files: {len(final_state.generated_files)}")
    print(f"  - Build steps: {len(final_state.build_steps)}")
    
    # Show unimplemented capabilities
    unimplemented = [c for c in final_state.capabilities if not c.implemented]
    if unimplemented:
        print(f"\n60 Unimplemented capabilities:")
        for cap in unimplemented:
            print(f"  - {cap.name}: {cap.file_path}")
    else:
        print("\n73 All capabilities implemented!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
