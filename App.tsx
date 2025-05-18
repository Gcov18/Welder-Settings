// NOTE: This file is intended for a mobile app (iOS/Android) only.
// For web, a separate app will be created.

import React, { useState } from 'react';
import { View, Text, TextInput, StyleSheet } from 'react-native';
import { Picker } from '@react-native-picker/picker';

type Process = 'MIG' | 'TIG' | 'Stick';
type Material = 'Steel' | 'Aluminum' | 'Stainless';

const processes: Process[] = ['MIG', 'TIG', 'Stick'];
const materials: Material[] = ['Steel', 'Aluminum', 'Stainless'];

function getSettings(process: Process, material: Material, thickness: number) {
    // Simple example logic for settings
    if (process === 'MIG' && material === 'Steel') {
        return {
            voltage: (thickness * 4).toFixed(1),
            amperage: (thickness * 30).toFixed(0),
            wireSpeed: (thickness * 2).toFixed(1),
            gas: '75% Argon / 25% CO2'
        };
    }
    // ...add more logic for other combinations...
    return {
        voltage: '-',
        amperage: '-',
        wireSpeed: '-',
        gas: '-'
    };
}

export default function App() {
    const [process, setProcess] = useState<Process>('MIG');
    const [material, setMaterial] = useState<Material>('Steel');
    const [thickness, setThickness] = useState<string>('0.125');

    const numericThickness = parseFloat(thickness) || 0;
    const settings = getSettings(process, material, numericThickness);

    return (
        <View style={styles.container}>
            <Text style={styles.header}>Welder Settings</Text>
            <Text style={styles.label}>Process:</Text>
            <Picker
                selectedValue={process}
                onValueChange={itemValue => setProcess(itemValue as Process)}
                style={styles.picker}
            >
                {processes.map(p => (
                    <Picker.Item key={p} label={p} value={p} />
                ))}
            </Picker>
            <Text style={styles.label}>Material:</Text>
            <Picker
                selectedValue={material}
                onValueChange={itemValue => setMaterial(itemValue as Material)}
                style={styles.picker}
            >
                {materials.map(m => (
                    <Picker.Item key={m} label={m} value={m} />
                ))}
            </Picker>
            <Text style={styles.label}>Thickness (inches):</Text>
            <TextInput
                style={styles.input}
                keyboardType="numeric"
                value={thickness}
                onChangeText={setThickness}
                placeholder="e.g. 0.125"
            />
            <View style={styles.divider} />
            <Text style={styles.subheader}>Recommended Settings</Text>
            <Text>Voltage: {settings.voltage} V</Text>
            <Text>Amperage: {settings.amperage} A</Text>
            <Text>Wire Speed: {settings.wireSpeed} in/min</Text>
            <Text>Gas: {settings.gas}</Text>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        width: '100%',
        maxWidth: 400,
        alignSelf: 'center',
        padding: 20,
        flex: 1,
        justifyContent: 'flex-start',
        backgroundColor: '#fff'
    },
    header: {
        fontSize: 24,
        fontWeight: 'bold',
        marginBottom: 16
    },
    subheader: {
        fontSize: 18,
        fontWeight: 'bold',
        marginTop: 16,
        marginBottom: 8
    },
    label: {
        marginTop: 12,
        marginBottom: 4,
        fontWeight: '500'
    },
    picker: {
        height: 44,
        width: '100%'
    },
    input: {
        borderWidth: 1,
        borderColor: '#ccc',
        borderRadius: 4,
        padding: 8,
        marginBottom: 8
    },
    divider: {
        height: 1,
        backgroundColor: '#ccc',
        marginVertical: 16
    }
});
