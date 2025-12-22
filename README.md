# UIOT Home Integration for Home Assistant

[English](./README.md) | [简体中文](./README_zh.md)

The UIOT integration is an officially supported Home Assistant integration provided by UIOT. It allows you to use UIOT's smart home devices within Home Assistant.

## Installation

Please install it using the following method:

### Method 1:Install via HACS

> 1. make sure you have installed HACS to Home Assistant [HACS install guide](https://hacs.xyz/docs/use/download/download/)
> 2. open HACS, click [Custom repositories], Repository input: `https://github.com/uiotlink/ha_uiot_home`, Category select [Integration]
> 3. **Restart Home Assistant**.


### Method 2:Manual Install

>1. Download `uiot_home.zip` from [Latest Release](https://github.com/uiotlink/ha_uiot_home/releases/latest)
>2. Unzip and copy `uiot_home` to `/custom_components/`. in Home Assistant.
>3. **Restart Home Assistant**.

## Configuration

### Login

[Settings > Devices & Services > Add Integration] > Search for “Uiot Home” > Next > Click here to log in > Log in using your UIOT account credentials. Note: Your account must already have a functioning UIOT host added.

### Device synchronization

After logging in successfully, a list of all host families under the user's account will pop up. Select the family you need to bind, and after submission, all currently supported devices under that family will be automatically synchronized.

## Supported devices

| Name                                                         | Function                                                     |
| :----------------------------------------------------------- | ------------------------------------------------------------ |
| Zero-fire single switch                                      | switch                                                       |
| Zero-fire double switch                                      | switch                                                       |
| Zero-fire triple switch                                      | switch                                                       |
| Zero-fire four switch                                        | switch                                                       |
| Smart light strip controller                                 | switch、brightness、color temperature、color                 |
| Smart color temperature light controller                     | switch、brightness、color temperature                        |
| Smart dimming controller                                     | switch、brightness                                           |
| Dimmer switch                                                | switch、brightness、color temperature                        |
| Smart spotlight                                              | switch、brightness、color temperature                        |
| Smart door/window sensor                                     | battery level、working mode、 opening and closing status     |
| Infrared curtain detector                                    | battery level、 light intensity、 alarm status               |
| AI super sensor                                              | working mode、 lighting、 body movement characteristics、 whether there are people or not |
| Dual-detection sensor                                        | working mode、 lighting、 body movement characteristics、 whether there are people or not |
| Temperature and humidity sensor                              | battery power、 temperature and humidity status              |
| Four-in-one air box（PM2.5）                                 | light、 temperature、 humidity、pm2.5                        |
| Four-in-one air sensor（PM2.5）                              | light、 temperature、 humidity、pm2.5                        |
| Four-in-one air sensor（formaldehyde）                       | light、 temperature、 humidity、formaldehyde                 |
| Four-in-one air sensor（CO2）                                | light、 temperature、 humidity、co2                          |
| Five-in-one air sensor（CO2）                                | light、 temperature、 humidity、co2、TVOC                    |
| Seven-in-one air box                                         | light、 temperature、 humidity、co2、pm2.5、noise、formaldehyde |
| Seven-in-one air box（TVOC）                                 | light、 temperature、 humidity、co2、pm2.5、noise、TVOC      |
| Seven-in-one air sensor                                      | light、 temperature、 humidity、co2、pm2.5、noise、formaldehyde |
| Seven-in-one air sensor（TVOC）                              | light、 temperature、 humidity、co2、pm2.5、noise、TVOC      |
| Eight-in-one air box                                         | light、 temperature、 humidity、co2、pm2.5、noise、formaldehyde、TVOC |
| Eight-in-one air sensor                                      | light、 temperature、 humidity、co2、pm2.5、noise、formaldehyde、TVOC |
| Single-channel motor panel                                   | on、off、pause                                               |
| Dual-channel motor panel                                     | on、off、pause                                               |
| Smart curtain motor                                          | on、off、pause、opening and closing degree                   |
| Smart roller blind motor                                     | on、off、pause、opening and closing degree                   |
| Lithium battery smart curtain motor                          | on、off、pause、opening and closing degree                   |
| Smart sliding window opener                                  | on、off、pause、opening and closing degree                   |
| Smart push-pull window opener                                | on、off、pause、opening and closing degree                   |
| Dooya tubular motor control box                              | on、off、pause、opening and closing degree                   |
| Dream curtain motor                                          | on、off、pause、opening and closing degree、rotation angle   |
| Six-in-one air sensor                                        | light、 temperature、 humidity、co2、pm2.5、noise            |
| Water leak detector                                          | Battery Level 、Alarm Status                                 |
| Smoke detector                                               | Battery Level 、Alarm Status                                 |
| Combustible gas detector                                     | Battery Level 、Alarm Status                                 |
| Emergency button                                             | Battery Level 、Alarm Status                                 |
| 3-in-1 Smart Thermostat Control Series                       | Air conditioning (on, off, mode, temperature, wind speed), strong current fresh air (on, off, wind speed), water floor heating (on, off, temperature) |
| 3-in-1 Premium Smart Thermostat Series                       | Air conditioning (on, off, mode, temperature, wind speed), strong current fresh air (on, off, wind speed), water floor heating (on, off, temperature) |
| Central Air Conditioning intelligent Gateway Engineering version | on、off、mode、 temperature、wind speed                      |
| Universal version of intelligent Gateway for Central Air conditioning | on、off、mode、 temperature、wind speed                      |
| Air conditioning thermostat E series                         | on、off、mode、 temperature、wind speed                      |
| Fresh air temperature controller E series                    | on、off、wind speed                                          |
| Fresh air temperature controller                             | on、off、wind speed                                          |
| Water heating thermostat E                                   | on, off, temperature                                         |
| Water floor heating thermostat                               | on、 off、 temperature                                       |
| Water floor heating thermostat (3H1)                         | on、 off、temperature                                        |
| Intelligent socket                                           | on、off                                                      |
| Infrared smart socket                                        | on、 off、Codebase air conditioning                          |
| Codebase air conditioning                                    | on、off、mode、 temperature、wind speed                      |
| Scene                                                        | Synchronize the scenarios set by the UIOT APP                |
| Three-in-one temperature controller C                        | Air conditioner (on, off, mode, temperature, wind speed), brand fresh air system (on, off, wind speed), electric floor heating (on, off, temperature) |
| Full-screen Air Conditioning Gateway C/S/E                   | Brand air conditioners (on/off, mode, temperature, wind speed) |
| Super Temperature Controller E                               | Brand air conditioners (on/off, mode, temperature, wind speed), brand fresh air (on/off, wind speed), strong current fresh air (on/off, wind speed), fan coil units (on/off, mode, temperature, wind speed) |
| Floor heating panel                                          | Water floor heating (on/off, temperature), Electric floor heating (on/off, temperature) |
| Composite panel                                              | Switch, curtain motor (on, off, pause)                       |
| Intelligent magnetic color temperature lamp                  | switch、brightness、color temperature                        |
| DALI dimming lamp                                            | switch、brightness                                           |
| DALI color temperature lamp                                  | switch、brightness、color temperature                        |
| Hvac control module                                          | Brand air conditioners (on, off, mode, temperature, wind speed), brand fresh air systems (on, off, wind speed), brand floor heating (on, off, temperature) |
| Smart voice Speaker X10                                      | Voice control of devices in HA (plug-in supported, ready for use after platform upgrade) |
| Fan coil unit temperature controller (3H1)                   | on、off、mode、 temperature、wind speed                      |
| Intelligent color-changing light                             | switch、brightness、color temperature、color                 |
| Intelligent dimming spotlight                                | switch、brightness                                           |
| Central Air Conditioning Smart Gateway PRO                   | on、off、mode、 temperature、wind speed                      |
| Switch Intelligent Controller Type Ⅰ                         | switch                                                       |
| Switch Intelligent Controller Type Ⅱ                         | switch                                                       |
| Switch Intelligent Controller Type Ⅲ                         | switch                                                       |
| Single-circuit switch (single fire) E series                 | switch                                                       |
| Dual-circuit switch (single fire) E series                   | switch                                                       |
| Three-way switch (single fire) E series                      | switch                                                       |
| Fan Coil (dual supply)                                       | switch、mode、 temperature、wind speed                       |
| Smart Water Floor Heating Thermostat                         | switch、 temperature                                         |
| AI human sensor                                              | light、Working Mode、Alarm Status、 Whether there are people or not |
| AI Super Sensor Pro                                          | light、Working Mode、Alarm Status、 Whether there are people or not、Detection distance |
| AI smart screen-switch                                       | switch                                                       |
| AI smart screen-curtain                                      | switch                                                       |
| AI smart screenA7/E-switch                                   | switch                                                       |
| AI smart screenA11/A13-switch                                | switch                                                       |
| AI smart screenC/S-switch                                    | switch                                                       |
| Smart color temperature light controller(0-10V)              | switch、brightness、color temperature                        |
| Hvac general module - Fan coil                               | on、off、mode、Wind speed、Temperature                       |
| Hvac general module - Fresh Air 3                            | on、off、Wind speed                                          |
| Hvac general module - Fresh Air 2                            | on、off、Wind speed                                          |
| Hvac general module - Water floor heating                    | on、off、Temperature                                         |
| Hvac general module - switch                                 | switch                                                       |
| Hvac general module - Garage door                            | switch                                                       |
| Infrared human detector                                      | Battery Level、Working Mode、Alarm Status、 Whether there are people or not |
| Infrared curtain detector                                    | Battery Level、Working Mode、Alarm Status、 Whether there are people or not |
| Wired infrared curtain detector                              | Working Mode、Alarm Status、 Whether there are people or not |
| Infrared curtain sensor                                      | Battery Level、Working Mode、Alarm Status、 Whether there are people or not |

## FAQ

### Q1:4.0 Account login prompt: Failed to obtain the token

- For the 4.0 host (UIOT Smart Home App), please check if you have registered an account for version 5.0 (Super Smart Home App). If you have, you need to log in to the Super Smart Home App to cancel the account for version 5.0

### Q2:The home name interface does not show the host name, and when you click Submit, an Unkown error occurred appears

- Check the "About" section on the App to see if an alias has been set for the server. If no alias has been set, you need to set an individual name and log in again to submit

### Q3:Which brands of air conditioners, fresh air systems and floor heating systems are currently supported
- Brand air conditioners: Gree Air Conditioner FGR3.5D, Hitachi Air Conditioner PC-PIHHQ, Haier Casarte YCJ-A001
- Brand fresh air systems: Adis Fresh Air KF-800RM, Boluo Fresh Air CS2, Jinuo Fresh Air
- Brand floor heating: Orig water floor heating, Orig electric floor heating, YaTeLee6606 floor heating
