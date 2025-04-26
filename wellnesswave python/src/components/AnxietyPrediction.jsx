import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';

const API_BASE_URL = "http://127.0.0.1:5001";

const Container = styled.div`
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 2rem;
`;

const FormCard = styled.div`
  background: white;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  padding: 2.5rem;
  width: 100%;
  max-width: 800px;
`;

const Title = styled.h1`
  color: #2c3e50;
  text-align: center;
  margin-bottom: 2rem;
  font-size: 2.5rem;
  font-weight: 700;
  position: relative;
  
  &::after {
    content: '';
    position: absolute;
    bottom: -10px;
    left: 50%;
    transform: translateX(-50%);
    width: 100px;
    height: 4px;
    background: linear-gradient(90deg, #3498db, #2ecc71);
    border-radius: 2px;
  }
`;

const ErrorMessage = styled.div`
  background: #ffebee;
  color: #c62828;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
`;

const QuestionGroup = styled.div`
  margin-bottom: 2rem;
  padding: 1.5rem;
  border-radius: 8px;
  background: #f8f9fa;
  
  &:hover {
    background: #f0f2f5;
  }
`;

const QuestionLabel = styled.label`
  display: block;
  margin-bottom: 1rem;
  color: #34495e;
  font-weight: 600;
  font-size: 1.1rem;
`;

const OptionsContainer = styled.div`
  display: flex;
  justify-content: space-between;
  gap: 1rem;
`;

const RadioOption = styled.div`
  flex: 1;
  text-align: center;
`;

const RadioInput = styled.input`
  cursor: pointer;
  margin-bottom: 0.5rem;
`;

const SubmitButton = styled.button`
  width: 100%;
  padding: 1rem;
  background: ${props => props.disabled ? '#bdc3c7' : 'linear-gradient(90deg, #3498db, #2ecc71)'};
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: ${props => props.disabled ? 'not-allowed' : 'pointer'};
  transition: all 0.3s ease;
  
  &:hover {
    transform: ${props => props.disabled ? 'none' : 'translateY(-2px)'};
    box-shadow: ${props => props.disabled ? 'none' : '0 5px 15px rgba(0, 0, 0, 0.1)'};
  }
`;

const ResultContainer = styled.div`
  margin-top: 2rem;
  padding: 2rem;
  border-radius: 12px;
  background: white;
  border: 3px solid ${props => props.borderColor};
`;

const ProgressBar = styled.div`
  width: 100%;
  height: 20px;
  background: #f0f0f0;
  border-radius: 10px;
  overflow: hidden;
  margin: 1rem 0;
  
  div {
    height: 100%;
    background: ${props => props.color};
    width: ${props => props.progress}%;
    transition: width 1s ease-in-out;
  }
`;

const SymptomList = styled.ul`
  list-style: none;
  padding: 0;
  margin: 1rem 0;
`;

const SymptomItem = styled.li`
  padding: 0.5rem;
  margin: 0.5rem 0;
  background: #f8f9fa;
  border-radius: 4px;
  color: #2c3e50;
`;

const AnxietyPrediction = () => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [serverStatus, setServerStatus] = useState({
    status: "Checking...",
    model_loaded: false
  });

  const questions = [
    { text: "Feeling nervous, anxious, or on edge", key: "nervousness" },
    { text: "Experiencing panic attacks", key: "panic_attacks" },
    { text: "Trouble relaxing", key: "trouble_relaxing" },
    { text: "Avoiding social situations", key: "social_avoidance" },
    { text: "Excessive worrying", key: "excessive_worry" },
    { text: "Difficulty sleeping", key: "sleep_difficulty" },
    { text: "Feeling lightheaded or dizzy", key: "lightheadedness" },
    { text: "Physical symptoms (racing heart, sweating)", key: "physical_symptoms" },
    { text: "Trouble concentrating", key: "concentration_issues" },
    { text: "Feeling impending doom", key: "impending_doom" }
  ];

  const [answers, setAnswers] = useState(Array(questions.length).fill(""));

  const answerOptions = [
    { value: "1", label: "Not at all", score: 1 },
    { value: "2", label: "Several days", score: 2 },
    { value: "3", label: "More than half the days", score: 3 },
    { value: "4", label: "Nearly every day", score: 4 },
    { value: "5", label: "Almost constantly", score: 5 }
  ];

  useEffect(() => {
    const checkServerStatus = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/test`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();
        setServerStatus(data);
      } catch (error) {
        console.error("Server check error:", error);
        setServerStatus({
          status: "Server not responding",
          model_loaded: false
        });
      }
    };

    checkServerStatus();
    const intervalId = setInterval(checkServerStatus, 30000);
    return () => clearInterval(intervalId);
  }, []);

  const handleAnswerChange = (index, value) => {
    const newAnswers = [...answers];
    newAnswers[index] = value;
    setAnswers(newAnswers);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (answers.includes("")) {
      setError("Please answer all questions before submitting.");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const formattedAnswers = questions.map((question, index) => ({
        question: question.key,
        answer: parseInt(answers[index]) // Convert to number
      }));

      console.log('Submitting answers:', formattedAnswers);

      const response = await fetch(`${API_BASE_URL}/predict/anxiety`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ answers: formattedAnswers }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Received data:', data);
      
      if (data.error) {
        throw new Error(data.error);
      }

      setResult(data);
    } catch (error) {
      console.error("Error:", error);
      setError(error.message || "An error occurred while processing your request. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const getResultColor = () => {
    if (!result) return "#4caf50";
    const level = result.category.toLowerCase();
    if (level.includes("no anxiety")) return "#4caf50";
    if (level.includes("mild")) return "#ff9800";
    if (level.includes("moderate")) return "#f57c00";
    if (level.includes("severe")) return "#e65100";
    return "#d32f2f";
  };

  return (
    <Container>
      <FormCard>
        <Title>Anxiety Assessment</Title>

        {error && <ErrorMessage>{error}</ErrorMessage>}

        {!result ? (
          <form onSubmit={handleSubmit}>
            {questions.map((question, index) => (
              <QuestionGroup key={index}>
                <QuestionLabel>{question.text}</QuestionLabel>
                <OptionsContainer>
                  {answerOptions.map(option => (
                    <RadioOption key={option.value}>
                      <RadioInput
                        type="radio"
                        name={`question-${index}`}
                        value={option.value}
                        checked={answers[index] === option.value}
                        onChange={() => handleAnswerChange(index, option.value)}
                      />
                      <span>{option.label}</span>
                    </RadioOption>
                  ))}
                </OptionsContainer>
              </QuestionGroup>
            ))}

            <SubmitButton
              type="submit"
              disabled={loading || !serverStatus.model_loaded}
            >
              {loading ? "Processing..." : "Submit Assessment"}
            </SubmitButton>
          </form>
        ) : (
          <ResultContainer borderColor={getResultColor()}>
            <h3>Assessment Result</h3>
            <p>Anxiety Level: <strong>{result.category}</strong></p>
            <ProgressBar color={getResultColor()} progress={result.probability * 100}>
              <div />
            </ProgressBar>
            <p>Confidence: {(result.probability * 100).toFixed(2)}%</p>

            <div style={{ marginTop: "2rem" }}>
              <h4>Symptom Summary</h4>
              
              {result.symptom_summary && (
                <>
                  {result.symptom_summary.severe_symptoms.length > 0 && (
                    <div>
                      <h5>Severe Symptoms</h5>
                      <SymptomList>
                        {result.symptom_summary.severe_symptoms.map((symptom, index) => (
                          <SymptomItem key={index}>{symptom}</SymptomItem>
                        ))}
                      </SymptomList>
                    </div>
                  )}
                  
                  {result.symptom_summary.moderate_symptoms.length > 0 && (
                    <div>
                      <h5>Moderate Symptoms</h5>
                      <SymptomList>
                        {result.symptom_summary.moderate_symptoms.map((symptom, index) => (
                          <SymptomItem key={index}>{symptom}</SymptomItem>
                        ))}
                      </SymptomList>
                    </div>
                  )}
                  
                  {result.symptom_summary.mild_symptoms.length > 0 && (
                    <div>
                      <h5>Mild Symptoms</h5>
                      <SymptomList>
                        {result.symptom_summary.mild_symptoms.map((symptom, index) => (
                          <SymptomItem key={index}>{symptom}</SymptomItem>
                        ))}
                      </SymptomList>
                    </div>
                  )}
                </>
              )}
            </div>

            <SubmitButton
              onClick={() => {
                setResult(null);
                setAnswers(Array(questions.length).fill(""));
              }}
              style={{ marginTop: "2rem" }}
            >
              Take Assessment Again
            </SubmitButton>
          </ResultContainer>
        )}
      </FormCard>
    </Container>
  );
};

export default AnxietyPrediction; 