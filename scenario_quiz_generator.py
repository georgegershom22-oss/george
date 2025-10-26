#!/usr/bin/env python3
"""
Banking Security Scenario Quiz Generator
Generates realistic scenario-based quiz questions for objective behavioral measurement.
These scenarios are used to create the objective_score variable in the dataset.
"""

import random
import json

def generate_scenario_quiz():
    """Generate comprehensive scenario-based quiz for objective behavioral measurement"""
    
    scenarios = [
        {
            "id": 1,
            "scenario": "You receive this SMS: 'Your account is locked. Click here to secure it: bit.ly/secure-now' What do you do?",
            "options": [
                {"text": "Click the link immediately", "score": 0, "explanation": "High risk - could be phishing"},
                {"text": "Call your bank using the number on your card", "score": 2, "explanation": "Best practice - use official contact"},
                {"text": "Ignore it", "score": 1, "explanation": "Safe but not optimal - should verify with bank"},
                {"text": "Reply to the SMS asking for more info", "score": 0, "explanation": "High risk - never reply to suspicious messages"}
            ],
            "correct_answer": 1
        },
        {
            "id": 2,
            "scenario": "You're at a coffee shop using public WiFi. You need to check your bank balance. What do you do?",
            "options": [
                {"text": "Log in immediately using the banking app", "score": 0, "explanation": "High risk - public WiFi is insecure"},
                {"text": "Wait until you get home to use secure WiFi", "score": 2, "explanation": "Best practice - avoid public WiFi for banking"},
                {"text": "Use the banking website with HTTPS", "score": 1, "explanation": "Better than app on public WiFi, but still risky"},
                {"text": "Use mobile data instead of WiFi", "score": 2, "explanation": "Good alternative - mobile data is more secure"}
            ],
            "correct_answer": 1
        },
        {
            "id": 3,
            "scenario": "You receive an email claiming to be from your bank asking you to update your password. What do you do?",
            "options": [
                {"text": "Click the link in the email and update password", "score": 0, "explanation": "High risk - could be phishing email"},
                {"text": "Log into your bank account directly (not via email link) to check", "score": 2, "explanation": "Best practice - verify through official channels"},
                {"text": "Reply to the email asking for verification", "score": 0, "explanation": "High risk - never reply to suspicious emails"},
                {"text": "Ignore the email completely", "score": 1, "explanation": "Safe but should verify if it's legitimate"}
            ],
            "correct_answer": 1
        },
        {
            "id": 4,
            "scenario": "Your banking app asks if you want to enable biometric login (fingerprint/face). What do you do?",
            "options": [
                {"text": "Enable it immediately", "score": 2, "explanation": "Good practice - biometrics are secure and convenient"},
                {"text": "Enable it but also keep password as backup", "score": 2, "explanation": "Excellent - layered security approach"},
                {"text": "Skip it and stick with password only", "score": 1, "explanation": "Acceptable but missing security benefits"},
                {"text": "Disable it because it's less secure", "score": 0, "explanation": "Incorrect - biometrics are generally more secure than passwords"}
            ],
            "correct_answer": 1
        },
        {
            "id": 5,
            "scenario": "You notice a small charge ($2.50) on your statement from an unknown merchant. What do you do?",
            "options": [
                {"text": "Ignore it - it's such a small amount", "score": 0, "explanation": "Risky - small charges can be test transactions"},
                {"text": "Call your bank immediately to report it", "score": 2, "explanation": "Best practice - report all suspicious activity"},
                {"text": "Wait to see if more charges appear", "score": 0, "explanation": "Risky - delay allows fraud to continue"},
                {"text": "Check if you made any recent small purchases", "score": 1, "explanation": "Good first step, but should still verify with bank"}
            ],
            "correct_answer": 1
        },
        {
            "id": 6,
            "scenario": "Your bank sends you a text with a verification code. You're expecting this code. What do you do?",
            "options": [
                {"text": "Enter the code immediately when prompted", "score": 2, "explanation": "Correct - you initiated the transaction"},
                {"text": "Wait 5 minutes before entering the code", "score": 1, "explanation": "Unnecessary delay - codes expire quickly"},
                {"text": "Call the bank to verify the code is legitimate", "score": 1, "explanation": "Overly cautious - you initiated the transaction"},
                {"text": "Ignore the code and try again later", "score": 0, "explanation": "Inefficient - codes are time-sensitive"}
            ],
            "correct_answer": 0
        },
        {
            "id": 7,
            "scenario": "You're setting up a new online account that requires banking information. What do you do?",
            "options": [
                {"text": "Provide your account number and routing number", "score": 1, "explanation": "Acceptable for legitimate services, but verify first"},
                {"text": "Use a payment service like PayPal instead", "score": 2, "explanation": "Better - adds security layer"},
                {"text": "Provide your full debit card number and PIN", "score": 0, "explanation": "High risk - never share PIN"},
                {"text": "Ask for alternative payment methods", "score": 2, "explanation": "Good - explore secure alternatives"}
            ],
            "correct_answer": 1
        },
        {
            "id": 8,
            "scenario": "You receive a call claiming to be from your bank's fraud department. They ask for your account number to verify your identity. What do you do?",
            "options": [
                {"text": "Provide your account number to verify", "score": 0, "explanation": "High risk - banks never call asking for account numbers"},
                {"text": "Ask for their employee ID and call back using the number on your card", "score": 2, "explanation": "Best practice - verify through official channels"},
                {"text": "Provide the last 4 digits only", "score": 1, "explanation": "Still risky - banks don't call asking for account info"},
                {"text": "Hang up and call your bank directly", "score": 2, "explanation": "Excellent - always initiate contact yourself"}
            ],
            "correct_answer": 1
        },
        {
            "id": 9,
            "scenario": "Your banking app offers to save your login credentials. What do you do?",
            "options": [
                {"text": "Save credentials for convenience", "score": 0, "explanation": "High risk - never save banking credentials"},
                {"text": "Save username only, not password", "score": 1, "explanation": "Better but still not recommended for banking"},
                {"text": "Use device biometrics instead of saving credentials", "score": 2, "explanation": "Best practice - biometrics are more secure"},
                {"text": "Never save any banking information", "score": 2, "explanation": "Excellent - maximum security approach"}
            ],
            "correct_answer": 2
        },
        {
            "id": 10,
            "scenario": "You're about to make a large transfer to a new payee. What do you do first?",
            "options": [
                {"text": "Make the transfer immediately", "score": 0, "explanation": "Risky - should verify payee first"},
                {"text": "Verify the payee's information through a separate channel", "score": 2, "explanation": "Best practice - always verify large transfers"},
                {"text": "Start with a small test transfer", "score": 1, "explanation": "Good practice but should still verify payee"},
                {"text": "Ask a family member to double-check", "score": 1, "explanation": "Good idea but should also verify independently"}
            ],
            "correct_answer": 1
        }
    ]
    
    return scenarios

def generate_quiz_instructions():
    """Generate instructions for the scenario-based quiz"""
    instructions = {
        "title": "Banking Security Behavior Assessment",
        "description": "This quiz measures your knowledge and behavioral tendencies regarding banking security practices. Each scenario presents a realistic banking situation. Choose the response that best reflects what you would actually do.",
        "instructions": [
            "Read each scenario carefully",
            "Consider what you would actually do in this situation",
            "Choose the response that best matches your likely behavior",
            "There are no 'trick' questions - answer honestly",
            "Your responses help measure real-world security behavior"
        ],
        "scoring": {
            "scale": "0-2 points per question",
            "total_possible": "20 points",
            "interpretation": {
                "18-20": "Excellent security behavior",
                "14-17": "Good security behavior", 
                "10-13": "Moderate security behavior",
                "6-9": "Below average security behavior",
                "0-5": "Poor security behavior"
            }
        }
    }
    return instructions

def save_quiz_data():
    """Save the complete quiz data to files"""
    scenarios = generate_scenario_quiz()
    instructions = generate_quiz_instructions()
    
    # Save scenarios as JSON
    with open('/workspace/banking_security_quiz_scenarios.json', 'w') as f:
        json.dump(scenarios, f, indent=2)
    
    # Save instructions as JSON
    with open('/workspace/banking_security_quiz_instructions.json', 'w') as f:
        json.dump(instructions, f, indent=2)
    
    # Create a human-readable version
    with open('/workspace/banking_security_quiz_readable.txt', 'w') as f:
        f.write("BANKING SECURITY BEHAVIOR QUIZ\n")
        f.write("=" * 50 + "\n\n")
        
        f.write("INSTRUCTIONS:\n")
        f.write("-" * 15 + "\n")
        for instruction in instructions['instructions']:
            f.write(f"• {instruction}\n")
        f.write("\n")
        
        f.write("SCORING:\n")
        f.write("-" * 10 + "\n")
        f.write(f"Scale: {instructions['scoring']['scale']}\n")
        f.write(f"Total Possible: {instructions['scoring']['total_possible']}\n\n")
        
        f.write("SCENARIOS:\n")
        f.write("-" * 12 + "\n\n")
        
        for scenario in scenarios:
            f.write(f"Scenario {scenario['id']}:\n")
            f.write(f"{scenario['scenario']}\n\n")
            
            for i, option in enumerate(scenario['options']):
                f.write(f"{chr(97+i)}) {option['text']}\n")
                f.write(f"   Score: {option['score']} - {option['explanation']}\n")
            
            f.write(f"\nCorrect Answer: {chr(97+scenario['correct_answer'])}\n")
            f.write("-" * 50 + "\n\n")
    
    print("Quiz data saved to:")
    print("- /workspace/banking_security_quiz_scenarios.json")
    print("- /workspace/banking_security_quiz_instructions.json") 
    print("- /workspace/banking_security_quiz_readable.txt")

def main():
    """Generate and save the complete quiz"""
    print("Generating Banking Security Scenario Quiz...")
    print("=" * 50)
    
    save_quiz_data()
    
    print("\nQuiz Generation Complete!")
    print("This quiz can be used to generate objective behavioral scores")
    print("for the banking security dataset.")

if __name__ == "__main__":
    main()