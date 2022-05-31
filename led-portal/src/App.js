import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';

import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Switch from '@mui/material/Switch';
import Slider from '@mui/material/Slider';
import Card from '@mui/material/Card';
import Checkbox from '@mui/material/Checkbox';
import { red, orange } from '@mui/material/colors';
import { ThemeProvider, createTheme } from '@mui/material/styles';

import Wheel from '@uiw/react-color-wheel';

import { GradientPicker } from 'react-linear-gradient-picker';
import 'react-linear-gradient-picker/dist/index.css';
import { Panel as ColorPicker } from 'rc-color-picker';


interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}


function rgb2hsv(r,g,b) {
  let v=Math.max(r,g,b), c=v-Math.min(r,g,b);
  let h= c && ((v==r) ? (g-b)/c : ((v==g) ? 2+(b-r)/c : 4+(r-g)/c));
  return [60*(h<0?h+6:h), v&&c/v, v];
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          <Typography>{children}</Typography>
        </Box>
      )}
    </div>
  );
}


function a11yProps(index: number) {
  return {
    id: `simple-tab-${index}`,
    'aria-controls': `simple-tabpanel-${index}`,
  };
}

const rgbToHsva = (rgb, a = 1) => {
  const list = rgb.match(/\d+/g);
  const hsv = rgb2hsv(list[0]/255., list[1]/255., list[2]/255.)
  return { h: hsv[0], s: Math.floor(hsv[1]*100), v: 68, a: a}
}

function componentToHex(c) {
  var hex = c.toString(16);
  return hex.length == 1 ? "0" + hex : hex;
}

const rgbToHex = (rgb, a = 1) => {
  const list = rgb.match(/\d+/g);
  return "#" + componentToHex(parseInt(list[0])) + componentToHex(parseInt(list[1])) + componentToHex(parseInt(list[2]));
}


class WrappedWheel extends Component{
 render() {
   return (
     <Wheel style={{marginTop:30, marginBottom:20}} color={rgbToHsva(this.props.color, this.props.opacity)} onChange={c => {
       // c.color is a hex code with #, c.alpha is 0-100
   		 this.props.onSelect(`rgb(${c.rgb.r},${c.rgb.g},${c.rgb.b})`, 1);
   	}}/>
   )
 }
}


class App extends Component {
  constructor(props) {
   super(props);
   this.state = {
     value: 0,
     on: true,
     brightness:255,
     solidColor:{ h: 0, s: 0, v: 68, a: 1 },
     solidColorHex:"#ffffff",
     rainbowSize:50,
     rainbowSpeed:50,
     gradientInverted:false,
     gradientPalette:[
        { offset: '0.00', color: 'rgb(238, 241, 11)' },
        { offset: '0.49', color: 'rgb(215, 128, 37)' },
        { offset: '1.00', color: 'rgb(126, 32, 207)' }
     ],
     cycleSpeed:50,
   };

   this.handleTabChange = this.handleTabChange.bind(this);
   this.handleOnOffChange = this.handleOnOffChange.bind(this);
   this.handleSliderBrightnessChange = this.handleSliderBrightnessChange.bind(this)
   this.handleSolidColorChange = this.handleSolidColorChange.bind(this)
   this.handleRainbowSliderSizeChange = this.handleRainbowSliderSizeChange.bind(this)
   this.handleRainbowSliderSpeedChange = this.handleRainbowSliderSpeedChange.bind(this)
   this.handleCycleSliderSpeedChange = this.handleCycleSliderSpeedChange.bind(this)
   this.handleGradientPaletteChange = this.handleGradientPaletteChange.bind(this)
   this.setStateAsync = this.setStateAsync.bind(this)
  }

  send() {
    let data = {};
    var route = "";
    if (this.state.value == 0) {
      route = "/solid";
      data['color'] = this.state.solidColorHex;
    }
    if (this.state.value == 1) {
      route = "/rainbow";
      data['speed'] = this.state.rainbowSpeed;
      data['width'] = this.state.rainbowSize;
    }
    if (this.state.value == 2) {
      route = "/gradient";
      let palette = this.state.gradientPalette.map((e)=>{return {offset: e.offset, color: rgbToHex(e.color)}})
      data['palette'] = palette;
      data['inverted'] = this.state.gradientInverted;
    }
    if (this.state.value == 3) {
      route = "/cycle";
      data['speed'] = this.state.cycleSpeed;
    }

    fetch(route, {
      body: data,
      headers: {"Content-Type": "application/json"},
      method: "POST"
    });
  }

  setStateAsync(state) {
      return new Promise((resolve) => {
        this.setState(state, resolve)
      });
  }

  handleSliderBrightnessChange(event: Event, newValue: number | number[]) {
    this.setState({brightness : newValue})
    let data = {};
    data['brightness'] = Math.floor(newValue * 255 / 100);
    fetch('/brightness', {
      body: data,
      headers: {"Content-Type": "application/json"},
      method: "POST"
    });
  };

  handleOnOffChange(event) {
    this.setStateAsync({on : event.target.checked}).then(()=>{
      fetch(this.state.on?"/on":"/off");
    })
  };

  handleSolidColorChange(color) {
    this.setStateAsync({solidColor : color.hsva, solidColorHex : color.hex}).then(()=>{
      this.send()
    });
  }

  handleTabChange(event, newValue) {
    this.setStateAsync({value : newValue}).then(()=>{
      this.send()
    });
  };

  handleRainbowSliderSizeChange(event: Event, newValue: number | number[]) {
    this.setStateAsync({rainbowSize : newValue}).then(()=>{
      this.send()
    });
  }

  handleRainbowSliderSpeedChange(event: Event, newValue: number | number[]) {
    this.setStateAsync({rainbowSpeed : newValue}).then(()=>{
      this.send()
    });
  }

  handleCycleSliderSpeedChange(event: Event, newValue: number | number[]) {
    this.setStateAsync({cycleSpeed : newValue}).then(()=>{
      this.send()
    });
  }

  handleGradientPaletteChange(palette) {
    this.setStateAsync({gradientPalette: palette}).then(()=>{
      this.send()
    });
  }

  handleGradientInvertedChange(event: Event, newValue: number | number[]) {

  }

  render() {
    return (
      <main className="App" style={{padding:10, backgroundColor:"#121212", height:"100%", alignItems:"center", justifyContent:"center"}}>
        <div style={{maxWidth:600, margin: "auto", alignSelf:"center"}}>
          <Card style={{margin:20}}>
            <Typography sx={{ fontSize: 22 }} color="text.primary" gutterBottom>
              On / Off
            </Typography>
            <Switch
              checked={this.state.on}
              onChange={this.handleOnOffChange}
              label="Disabled" defaultChecked />
          </Card>
          <Card style={{margin:20}}>
            <Typography sx={{ fontSize: 22 }} color="text.primary" gutterBottom>
              Brightness
            </Typography>
            <div style={{margin:30}}>
              <Slider defaultValue={50} aria-label="Brightness" valueLabelDisplay="auto" onChange={this.handleSliderBrightnessChange}/>
            </div>
          </Card>
          <Card style={{margin:20}}>
            <Typography sx={{ fontSize: 22 }} color="text.primary" gutterBottom>
              Color & Effects
            </Typography>
            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
              <Tabs variant="fullWidth" value={this.state.value} onChange={this.handleTabChange} aria-label="tabs">
                <Tab label="Solid" {...a11yProps(0)} />
                <Tab label="Rainbow" {...a11yProps(1)} />
                <Tab label="Gradient" {...a11yProps(2)} />
                <Tab label="Cycle" {...a11yProps(3)} />
              </Tabs>
            </Box>
            <TabPanel value={this.state.value} index={0}>
              <div style={{margin:"auto", display:"flex", justifyContent:"center", alignItems:"center"}}>
                <Wheel
                  color={this.state.solidColor}
                  onChange={this.handleSolidColorChange}
                />
              </div>
            </TabPanel>
            <TabPanel value={this.state.value} index={1}>
              <div style={{margin:30}}>
                <Typography sx={{ fontSize: 22 }} color="text.secondary" gutterBottom>
                  Size
                </Typography>
                <Slider defaultValue={50} aria-label="Size" size="small" valueLabelDisplay="auto" onChange={this.handleRainbowSliderSizeChange}/>
              </div>
              <div style={{margin:30}}>
                <Typography sx={{ fontSize: 22 }} color="text.secondary" gutterBottom>
                  Speed
                </Typography>
                <Slider defaultValue={50} aria-label="Speed" size="small" valueLabelDisplay="auto" onChange={this.handleRainbowSliderSpeedChange}/>
              </div>
            </TabPanel>
            <TabPanel value={this.state.value} index={2}>
              <GradientPicker {...{
                  width: 320,
                  paletteHeight: 32,
                  palette: this.state.gradientPalette,
                  onPaletteChange: this.handleGradientPaletteChange
              }}>
                  <WrappedWheel/>
              </GradientPicker>
              <div style={{display:"flex", flexDirection:"row", justifyContent:"center", alignItems:"center"}}>
                <Checkbox onChange={this.handleGradientInvertedChange}/>
                <Typography sx={{ fontSize: 22, marginBottom:.2 }} color="text.secondary" gutterBottom>
                  Inverted
                </Typography>
              </div>
            </TabPanel>
            <TabPanel value={this.state.value} index={3}>
              <div style={{margin:30}}>
                <Typography sx={{ fontSize: 22 }} color="text.secondary" gutterBottom>
                  Speed
                </Typography>
                <Slider defaultValue={50} aria-label="Speed" size="small" valueLabelDisplay="auto" onChange={this.handleCycleSliderSpeedChange}/>
              </div>
            </TabPanel>
          </Card>
        </div>
      </main>
    );
  }
}

const theme = createTheme({
  palette: {
    mode: 'dark',
  },
  status: {
    danger: orange[500],
  },
});

function ThemedApp() {
  return <ThemeProvider theme={theme}><App/></ThemeProvider>;
}
export default ThemedApp;
