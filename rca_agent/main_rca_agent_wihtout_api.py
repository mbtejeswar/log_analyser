from rca_service import perform_root_cause_analysis
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python main_rca_agent.py '<error_log_message>'")
        sys.exit(1)
    
    error_log = sys.argv[1]
    result = perform_root_cause_analysis(error_log)
    
    print("=== ROOT CAUSE ANALYSIS ===")
    print(f"Error: {result['error_log']}")
    print(f"Analysis: {result['analysis']}")
    if result['context_provided']:
        print("Relevant code context was found and used.")

if __name__ == "__main__":
    main()
