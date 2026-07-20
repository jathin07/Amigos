import React, { createContext, useContext, useState, useEffect } from 'react';
import { getDestinationTheme } from '../../data/destinationThemes';
import { apiFetch } from '../../config/api';

const SmartThemeContext = createContext(null);

const mockWeatherDatabase = {
  munnar: { temp: 18, condition: "Clouds", humidity: 84, wind_speed: 11, sunset: "6:42 PM" },
  ooty: { temp: 16, condition: "Clouds", humidity: 80, wind_speed: 12, sunset: "6:40 PM" },
  coorg: { temp: 20, condition: "Rain", humidity: 92, wind_speed: 15, sunset: "6:48 PM" },
  pondicherry: { temp: 31, condition: "Clear", humidity: 70, wind_speed: 18, sunset: "6:35 PM" },
  gokarna: { temp: 29, condition: "Clear", humidity: 74, wind_speed: 14, sunset: "6:52 PM" },
  wayanad: { temp: 22, condition: "Rain", humidity: 88, wind_speed: 9, sunset: "6:45 PM" }
};

const getMockWeather = (name) => {
  if (!name) return { temp: 24, condition: "Clear", humidity: 60, wind_speed: 10, sunset: "6:30 PM" };
  const key = name.toLowerCase().trim();
  return mockWeatherDatabase[key] || { temp: 24, condition: "Clear", humidity: 62, wind_speed: 11, sunset: "6:38 PM" };
};

export const DestinationThemeProvider = ({ destinationName, children }) => {
  const [themeData, setThemeData] = useState(null);
  const [weatherData, setWeatherData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isLive, setIsLive] = useState(false);
  const [mood, setMood] = useState(null);
  const [recommendations, setRecommendations] = useState([]);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setIsLive(false);

    const theme = getDestinationTheme(destinationName);
    setThemeData(theme);

    const fetchInsights = async () => {
      try {
        const name = (destinationName || '').toLowerCase().trim();
        const data = await apiFetch(`/destination_insights?q=${encodeURIComponent(name)}`);
        if (active) {
          setWeatherData(data.weather);
          setMood(data.mood);
          setRecommendations(data.recommendations || []);
          setIsLive(true);
          setLoading(false);
        }
      } catch (err) {
        console.warn('Failed to fetch live insights, falling back to static data:', err);
        if (active) {
          const weather = getMockWeather(destinationName);
          setWeatherData(weather);
          setMood('Calm');
          setRecommendations([]);
          setIsLive(false);
          setLoading(false);
        }
      }
    };

    fetchInsights();

    return () => { active = false; };
  }, [destinationName]);

  const activeCondition = weatherData?.condition || 'Default';
  const weatherTips = themeData?.weatherRules?.[activeCondition] || themeData?.weatherRules?.Default || {};

  return (
    <SmartThemeContext.Provider value={{
      themeData,
      weatherData,
      weatherTips,
      activeCondition,
      loading,
      isLive,
      mood,
      recommendations
    }}>
      {children}
    </SmartThemeContext.Provider>
  );
};

export const useSmartTheme = () => {
  const context = useContext(SmartThemeContext);
  if (!context) {
    throw new Error('useSmartTheme must be used within a DestinationThemeProvider');
  }
  return context;
};
