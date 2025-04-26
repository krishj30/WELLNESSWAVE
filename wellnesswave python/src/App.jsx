import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import DepressionForm from './components/DepressionForm';
import AnxietyPrediction from './components/AnxietyPrediction';
import styled from 'styled-components';

const NavContainer = styled.nav`
  background: #2c3e50;
  padding: 1rem;
  margin-bottom: 2rem;
`;

const NavList = styled.ul`
  list-style: none;
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin: 0;
  padding: 0;
`;

const NavItem = styled.li`
  a {
    color: white;
    text-decoration: none;
    font-size: 1.2rem;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    transition: background-color 0.3s;

    &:hover {
      background-color: #34495e;
    }
  }
`;

const AppContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
`;

function App() {
  return (
    <Router>
      <div>
        <NavContainer>
          <NavList>
            <NavItem>
              <Link to="/depression">Depression Assessment</Link>
            </NavItem>
            <NavItem>
              <Link to="/anxiety">Anxiety Assessment</Link>
            </NavItem>
          </NavList>
        </NavContainer>
        
        <AppContainer>
          <Routes>
            <Route path="/depression" element={<Depressionform />} />
            <Route path="/anxiety" element={<AnxietyPrediction />} />
            <Route path="/" element={<Depressionform />} />
          </Routes>
        </AppContainer>
      </div>
    </Router>
  );
}

export default App; 