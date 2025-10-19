#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Utility Functions for Acoustic Simulations in Abaqus
=====================================================
Helper functions for material properties, ocean stratification models,
and acoustic parameter calculations.
"""

import numpy as np
from scipy import interpolate
import math


class AcousticMaterialProperties:
    """
    Calculate acoustic material properties for various media
    """
    
    @staticmethod
    def water_properties(temperature, salinity=35.0, pressure=0.0):
        """
        Calculate water density and sound speed using UNESCO equations
        
        Parameters:
        -----------
        temperature : float
            Temperature in Celsius
        salinity : float
            Salinity in PSU (practical salinity units)
        pressure : float
            Pressure in dbar (1 dbar = 10 kPa)
            
        Returns:
        --------
        dict : Contains density (kg/m³), sound_speed (m/s), bulk_modulus (Pa)
        """
        T = temperature
        S = salinity
        P = pressure / 10.0  # Convert to bars
        
        # Density calculation (UNESCO equation of state)
        # Pure water density
        rho_w = (999.842594 + 6.793952e-2 * T 
                - 9.095290e-3 * T**2 
                + 1.001685e-4 * T**3 
                - 1.120083e-6 * T**4 
                + 6.536336e-9 * T**5)
        
        # Salinity correction
        A = (8.24493e-1 - 4.0899e-3 * T 
             + 7.6438e-5 * T**2 
             - 8.2467e-7 * T**3 
             + 5.3875e-9 * T**4)
        
        B = (-5.72466e-3 + 1.0227e-4 * T 
             - 1.6546e-6 * T**2)
        
        C = 4.8314e-4
        
        rho = rho_w + A * S + B * S**1.5 + C * S**2
        
        # Sound speed calculation (Chen-Millero-Li equation)
        c_0 = (1402.388 + 5.03830 * T 
               - 5.81090e-2 * T**2 
               + 3.3432e-4 * T**3 
               - 1.47797e-6 * T**4 
               + 3.1419e-9 * T**5)
        
        c_s = (0.163310 + 1.361000e-4 * T 
               + 5.46000e-6 * T**2 
               - 8.10000e-8 * T**3 
               + 7.00000e-10 * T**4) * S
        
        c_p = (1.389 - 1.262e-2 * T 
               + 7.166e-5 * T**2 
               + 2.008e-6 * T**3 
               - 3.21e-8 * T**4) * P / 1000.0
        
        c = c_0 + c_s + c_p
        
        # Bulk modulus
        K = rho * c * c
        
        return {
            'density': rho,
            'sound_speed': c,
            'bulk_modulus': K,
            'temperature': T,
            'salinity': S,
            'pressure': P
        }
    
    @staticmethod
    def air_properties(temperature=20.0, pressure=101325.0, humidity=0.5):
        """
        Calculate air density and sound speed
        
        Parameters:
        -----------
        temperature : float
            Temperature in Celsius
        pressure : float
            Atmospheric pressure in Pa
        humidity : float
            Relative humidity (0-1)
            
        Returns:
        --------
        dict : Contains density, sound_speed, bulk_modulus
        """
        T = temperature + 273.15  # Convert to Kelvin
        P = pressure
        RH = humidity
        
        # Gas constants
        R_air = 287.05  # J/(kg·K)
        R_vapor = 461.495  # J/(kg·K)
        
        # Saturation vapor pressure (Tetens formula)
        e_sat = 610.78 * np.exp(17.27 * temperature / (temperature + 237.3))
        
        # Actual vapor pressure
        e = RH * e_sat
        
        # Density
        rho_dry = (P - e) / (R_air * T)
        rho_vapor = e / (R_vapor * T)
        rho = rho_dry + rho_vapor
        
        # Sound speed (with humidity correction)
        gamma = 1.4  # Ratio of specific heats
        c_dry = np.sqrt(gamma * R_air * T)
        
        # Humidity correction factor
        h = e / P
        c = c_dry * np.sqrt(1 + 0.16 * h)
        
        # Bulk modulus
        K = rho * c * c
        
        return {
            'density': rho,
            'sound_speed': c,
            'bulk_modulus': K,
            'temperature': temperature,
            'pressure': P,
            'humidity': RH
        }


class OceanStratification:
    """
    Generate realistic ocean stratification profiles
    """
    
    @staticmethod
    def thermocline_profile(depths, surface_temp=25.0, deep_temp=4.0, 
                           thermocline_depth=100.0, thermocline_thickness=50.0):
        """
        Generate temperature profile with thermocline
        
        Parameters:
        -----------
        depths : array-like
            Depth points in meters
        surface_temp : float
            Surface temperature (°C)
        deep_temp : float
            Deep water temperature (°C)
        thermocline_depth : float
            Depth of thermocline center (m)
        thermocline_thickness : float
            Thickness of thermocline transition (m)
            
        Returns:
        --------
        array : Temperature at each depth
        """
        z = np.array(depths)
        T_surface = surface_temp
        T_deep = deep_temp
        z_therm = thermocline_depth
        dz_therm = thermocline_thickness
        
        # Hyperbolic tangent profile
        temperature = T_deep + (T_surface - T_deep) * 0.5 * (
            1 - np.tanh(2 * (z - z_therm) / dz_therm)
        )
        
        return temperature
    
    @staticmethod
    def halocline_profile(depths, surface_salinity=33.0, deep_salinity=35.0,
                         halocline_depth=50.0, halocline_thickness=20.0):
        """
        Generate salinity profile with halocline
        
        Parameters similar to thermocline_profile but for salinity (PSU)
        """
        z = np.array(depths)
        S_surface = surface_salinity
        S_deep = deep_salinity
        z_halo = halocline_depth
        dz_halo = halocline_thickness
        
        salinity = S_deep + (S_surface - S_deep) * 0.5 * (
            1 - np.tanh(2 * (z - z_halo) / dz_halo)
        )
        
        return salinity
    
    @staticmethod
    def canonical_deep_ocean(depths):
        """
        Generate canonical deep ocean sound speed profile
        
        Parameters:
        -----------
        depths : array-like
            Depth points in meters
            
        Returns:
        --------
        dict : Temperature, salinity, sound speed, density profiles
        """
        z = np.array(depths)
        
        # Munk canonical profile parameters
        z_axis = 1300.0  # Depth of sound speed minimum (m)
        B = 1.3e-3  # Inverse scale depth
        epsilon = 7.37e-3  # Perturbation strength
        c_axis = 1480.0  # Sound speed at axis (m/s)
        
        # Normalized depth
        eta = 2 * (z - z_axis) / B
        
        # Sound speed profile (Munk profile)
        c = c_axis * (1 + epsilon * (eta - 1 + np.exp(-eta)))
        
        # Approximate temperature from sound speed
        # Simplified inverse relationship
        temperature = 20.0 - (1520.0 - c) / 3.0
        
        # Salinity increases slightly with depth
        salinity = 34.5 + 0.5 * z / 5000.0
        
        # Calculate density using equation of state
        density = []
        for i, d in enumerate(z):
            props = AcousticMaterialProperties.water_properties(
                temperature[i], salinity[i], d/10.0
            )
            density.append(props['density'])
        
        return {
            'depth': z,
            'temperature': temperature,
            'salinity': salinity,
            'sound_speed': c,
            'density': np.array(density)
        }


class AcousticAbsorption:
    """
    Calculate frequency-dependent acoustic absorption in various media
    """
    
    @staticmethod
    def water_absorption_francois_garrison(frequency, temperature=10.0, 
                                          salinity=35.0, depth=0.0, pH=8.0):
        """
        Calculate seawater absorption using Francois-Garrison equations
        
        Parameters:
        -----------
        frequency : float or array
            Frequency in Hz
        temperature : float
            Temperature in Celsius
        salinity : float
            Salinity in PSU
        depth : float
            Depth in meters
        pH : float
            pH value (typically 8.0 for seawater)
            
        Returns:
        --------
        float or array : Absorption coefficient in dB/m
        """
        f = np.array(frequency) / 1000.0  # Convert to kHz
        T = temperature
        S = salinity
        D = depth / 1000.0  # Convert to km
        
        # Temperature dependence
        T_kelvin = T + 273.15
        
        # Boric acid contribution
        A1 = 8.86 / np.sqrt(S/35.0) * 10**(0.78 * pH - 5)
        P1 = 1.0
        f1 = 2.8 * np.sqrt(S/35.0) * 10**(4 - 1245/T_kelvin)
        
        alpha_1 = (A1 * P1 * f1 * f**2) / (f1**2 + f**2)
        
        # Magnesium sulfate contribution
        A2 = 21.44 * S / 35.0 * (1 + 0.025 * T)
        P2 = 1 - 1.37e-4 * D + 6.2e-9 * D**2
        f2 = 8.17 * 10**(8 - 1990/T_kelvin) / (1 + 0.0018 * (S - 35))
        
        alpha_2 = (A2 * P2 * f2 * f**2) / (f2**2 + f**2)
        
        # Pure water contribution
        if T <= 20:
            A3 = 4.937e-4 - 2.59e-5 * T + 9.11e-7 * T**2 - 1.50e-8 * T**3
        else:
            A3 = 3.964e-4 - 1.146e-5 * T + 1.45e-7 * T**2 - 6.5e-10 * T**3
            
        P3 = 1 - 3.83e-5 * D + 4.9e-10 * D**2
        
        alpha_3 = A3 * P3 * f**2
        
        # Total absorption in dB/km
        alpha_total = alpha_1 + alpha_2 + alpha_3
        
        # Convert to dB/m
        return alpha_total / 1000.0
    
    @staticmethod
    def air_absorption_iso9613(frequency, temperature=20.0, humidity=0.5, 
                               pressure=101325.0):
        """
        Calculate atmospheric absorption using ISO 9613-1
        
        Parameters:
        -----------
        frequency : float or array
            Frequency in Hz
        temperature : float
            Temperature in Celsius
        humidity : float
            Relative humidity (0-1)
        pressure : float
            Atmospheric pressure in Pa
            
        Returns:
        --------
        float or array : Absorption coefficient in dB/m
        """
        f = np.array(frequency)
        T = temperature + 273.15
        T_ref = 293.15
        T_01 = 273.16
        P = pressure
        P_ref = 101325.0
        h = humidity * 100.0  # Convert to percentage
        
        # Saturation pressure
        psat = P_ref * 10**(-6.8346 * (T_01/T)**1.261 + 4.6151)
        
        # Molar concentration of water vapor
        h_molar = h * (psat/P_ref) / (P/P_ref)
        
        # Relaxation frequencies
        f_rO = (P/P_ref) * (24 + 4.04e4 * h_molar * (0.02 + h_molar) / (0.391 + h_molar))
        f_rN = (P/P_ref) * (T/T_ref)**(-0.5) * (9 + 280 * h_molar * np.exp(-4.170 * ((T/T_ref)**(-1/3) - 1)))
        
        # Classical absorption
        alpha_cl = 1.84e-11 * (P_ref/P) * (T/T_ref)**0.5 * f**2
        
        # Molecular absorption
        alpha_rot = f**2 * (P/P_ref) * (T_ref/T)**2 * (
            1.60e-10 * np.exp(-11.2 * h_molar) +
            1.13e-7 * f_rO / (f_rO**2 + f**2) +
            5.50e-8 * f_rN / (f_rN**2 + f**2)
        )
        
        # Total absorption in dB/m
        alpha = 8.686 * (alpha_cl + alpha_rot)
        
        return alpha


class FieldVariableGenerator:
    """
    Generate field variable distributions for Abaqus
    """
    
    @staticmethod
    def linear_gradient(x, x_min=0.0, x_max=1.0):
        """Generate linear field variable from 0 to 1"""
        return (x - x_min) / (x_max - x_min)
    
    @staticmethod
    def exponential_gradient(x, x_min=0.0, x_max=1.0, rate=1.0):
        """Generate exponential field variable"""
        x_norm = (x - x_min) / (x_max - x_min)
        return (np.exp(rate * x_norm) - 1) / (np.exp(rate) - 1)
    
    @staticmethod
    def sinusoidal_variation(x, x_min=0.0, x_max=1.0, periods=1.0):
        """Generate sinusoidal field variable"""
        x_norm = (x - x_min) / (x_max - x_min)
        return 0.5 * (1 + np.sin(2 * np.pi * periods * x_norm - np.pi/2))
    
    @staticmethod
    def step_function(x, steps, x_min=0.0, x_max=1.0):
        """Generate step-wise field variable"""
        x_norm = (x - x_min) / (x_max - x_min)
        n_steps = len(steps) - 1
        step_size = 1.0 / n_steps
        
        field = np.zeros_like(x)
        for i in range(n_steps):
            mask = (x_norm >= i * step_size) & (x_norm < (i+1) * step_size)
            field[mask] = steps[i]
        field[x_norm >= 1.0] = steps[-1]
        
        return field
    
    @staticmethod
    def generate_abaqus_table(x_values, property_func, field_func=None):
        """
        Generate property table for Abaqus material definition
        
        Parameters:
        -----------
        x_values : array-like
            Spatial coordinates
        property_func : callable
            Function that returns property value given position
        field_func : callable
            Function that returns field variable given position
            
        Returns:
        --------
        list : Table entries as (property, field_variable) tuples
        """
        if field_func is None:
            field_func = FieldVariableGenerator.linear_gradient
            
        table = []
        for x in x_values:
            prop = property_func(x)
            field = field_func(x, x_values[0], x_values[-1])
            table.append((prop, field))
            
        return table


class TransmissionLossModels:
    """
    Theoretical models for transmission loss
    """
    
    @staticmethod
    def spherical_spreading(range_m, source_level=100.0):
        """TL = 20*log10(r) for spherical spreading"""
        r = np.maximum(range_m, 1.0)  # Avoid log(0)
        return source_level - 20 * np.log10(r)
    
    @staticmethod
    def cylindrical_spreading(range_m, source_level=100.0, transition_range=1.0):
        """TL = 10*log10(r) for cylindrical spreading (after transition)"""
        r = np.maximum(range_m, transition_range)
        tl = np.zeros_like(r)
        
        # Spherical spreading before transition
        mask_spherical = r <= transition_range
        tl[mask_spherical] = 20 * np.log10(r[mask_spherical])
        
        # Cylindrical spreading after transition
        mask_cylindrical = r > transition_range
        tl[mask_cylindrical] = (20 * np.log10(transition_range) + 
                               10 * np.log10(r[mask_cylindrical] / transition_range))
        
        return source_level - tl
    
    @staticmethod
    def thorp_absorption(frequency, range_km):
        """
        Thorp's formula for absorption loss in seawater
        
        Parameters:
        -----------
        frequency : float
            Frequency in kHz
        range_km : float
            Range in kilometers
            
        Returns:
        --------
        float : Absorption loss in dB
        """
        f = frequency
        
        # Thorp's formula (dB/km)
        if f < 1:
            alpha = 0.11 * f**2 / (1 + f**2)
        else:
            alpha = (0.11 * f**2 / (1 + f**2) + 
                    44 * f**2 / (4100 + f**2) +
                    2.75e-4 * f**2 + 0.003)
        
        return alpha * range_km


# Example usage and testing
if __name__ == "__main__":
    
    print("="*60)
    print("ACOUSTIC UTILITIES TEST")
    print("="*60)
    
    # Test water properties
    print("\n1. Water Properties at Different Conditions:")
    print("-" * 40)
    
    conditions = [
        (5, 35, 0),    # Cold surface water
        (20, 35, 0),   # Warm surface water
        (4, 35, 1000), # Deep water
    ]
    
    for T, S, P in conditions:
        props = AcousticMaterialProperties.water_properties(T, S, P)
        print(f"T={T}°C, S={S}PSU, P={P}dbar:")
        print(f"  ρ = {props['density']:.2f} kg/m³")
        print(f"  c = {props['sound_speed']:.2f} m/s")
        print(f"  K = {props['bulk_modulus']:.3e} Pa")
    
    # Test ocean stratification
    print("\n2. Ocean Stratification Profile:")
    print("-" * 40)
    
    depths = np.linspace(0, 500, 11)
    temps = OceanStratification.thermocline_profile(depths)
    
    print("Depth (m) | Temperature (°C)")
    for d, t in zip(depths, temps):
        print(f"{d:8.1f} | {t:8.2f}")
    
    # Test absorption
    print("\n3. Frequency-Dependent Absorption:")
    print("-" * 40)
    
    frequencies = np.array([100, 500, 1000, 5000, 10000])
    
    for f in frequencies:
        alpha = AcousticAbsorption.water_absorption_francois_garrison(f, 10, 35, 100)
        print(f"f = {f:5d} Hz: α = {alpha:.6f} dB/m = {alpha*1000:.3f} dB/km")
    
    # Test field variable generation
    print("\n4. Field Variable Distributions:")
    print("-" * 40)
    
    x = np.linspace(0, 10, 11)
    
    linear = FieldVariableGenerator.linear_gradient(x, 0, 10)
    exponential = FieldVariableGenerator.exponential_gradient(x, 0, 10, 2)
    
    print("x (m)  | Linear FV | Exp FV")
    for i in range(len(x)):
        print(f"{x[i]:6.1f} | {linear[i]:9.3f} | {exponential[i]:7.3f}")
    
    print("\n" + "="*60)
    print("UTILITIES TEST COMPLETED")
    print("="*60)