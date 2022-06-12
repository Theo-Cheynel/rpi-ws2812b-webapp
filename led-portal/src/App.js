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
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import AddAlarmIcon from '@mui/icons-material/AddAlarm';
import AlarmOnIcon from '@mui/icons-material/AlarmOn';
import AlarmOffIcon from '@mui/icons-material/AlarmOff';
import IconButton from '@mui/material/IconButton';
import DeleteIcon from '@mui/icons-material/Delete';
import ToggleButton from '@mui/material/ToggleButton';
import ToggleButtonGroup from '@mui/material/ToggleButtonGroup';

import BoltIcon from '@mui/icons-material/Bolt';
import MovingIcon from '@mui/icons-material/Moving';

//import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';

import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { StaticTimePicker } from '@mui/x-date-pickers/StaticTimePicker';
import { red, orange } from '@mui/material/colors';
import { ThemeProvider, createTheme } from '@mui/material/styles';

import Wheel from '@uiw/react-color-wheel';

import { GradientPicker } from 'react-linear-gradient-picker';
import 'react-linear-gradient-picker/dist/index.css';


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
  return { h: hsv[0], s: Math.floor(hsv[1]*100), v: 100, a: a}
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
     solidColor:{ h: 0, s: 0, v: 100, a: 1 },
     solidColorHex:"#ffffff",
     rainbowSize:50,
     rainbowSpeed:50,
     gradientInverted:false,
     gradientPalette:[
        { offset: '0.00', color: 'rgb(238, 255, 255)' },
        { offset: '0.49', color: 'rgb(215, 128, 37)' },
        { offset: '1.00', color: 'rgb(126, 32, 207)' }
     ],
     cycleSpeed:50,
     alarms:[],
     openingAlarmTimeSelector:false
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
   this.fetchState = this.fetchState.bind(this)
  }

  componentWillMount() {
    this.fetchState()
  }

  fetchState() {
    fetch('state', {mode: 'no-cors'})
    .then(response => {console.log(response); return response.json()})
    .then(data => {
      console.log(data)
      const values = {"solid" : 0, "rainbow" : 1, "gradient": 2, "cycle" : 3, "music" : 4}
      const color = rgb2hsv(data.solid.color[0]/255., data.solid.color[1]/255., data.solid.color[2]/255.)
      const state = {
        value : values[data.program],
        on : data.on,
        brightness : Math.floor(data.brightness / 255 * 100),
        solidColor : {h : Math.floor(color[0]), s : Math.floor(color[1] * 100), v : 100, a : 1},
        solidColorHex: "#" + componentToHex(parseInt(data.solid.color[0])) + componentToHex(parseInt(data.solid.color[1])) + componentToHex(parseInt(data.solid.color[2])),
        rainbowSize: data.rainbow.width,
        rainbowSpeed: data.rainbow.speed,
        //gradientInverted
        gradientPalette: data.gradient.palette.map(e=>{return {offset:e.offset, color:`rgb(${e.color[0]}, ${e.color[1]}, ${e.color[2]})`}}),
        cycleSpeed: data.cycle.speed,
      }
      console.log('state', state)
      this.setState(state)
    })
    .catch((error) => {
      console.error('Error:', error);
    })
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
    if (this.state.value == 4) {
      route = "/music";
    }

    fetch(route, {
      body: JSON.stringify(data),
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
      body: JSON.stringify(data),
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
      <main className="App" style={{padding:10, height:'100%', backgroundColor:"#121212", display:'flex', alignItems:"center", justifyContent:"center"}}>
        <div style={{maxWidth:window.innerWidth>1240?1200:600, backgroundColor:"#121212", margin: "auto", alignSelf:"center", display:'flex', flex:1, flexDirection:window.innerWidth>1240?'row':'column'}}>
          <div>
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
                <Slider value={this.state.brightness} min={1} max={100} defaultValue={50} aria-label="Brightness" valueLabelDisplay="auto" onChange={this.handleSliderBrightnessChange}/>
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
                  <Tab label="Music" {...a11yProps(4)} />
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
                  <Slider value={this.state.rainbowSize} min={1} max={100} defaultValue={50} aria-label="Size" size="small" valueLabelDisplay="auto" onChange={this.handleRainbowSliderSizeChange}/>
                </div>
                <div style={{margin:30}}>
                  <Typography sx={{ fontSize: 22 }} color="text.secondary" gutterBottom>
                    Speed
                  </Typography>
                  <Slider value={this.state.rainbowSpeed} min={1} max={100} defaultValue={50} aria-label="Speed" size="small" valueLabelDisplay="auto" onChange={this.handleRainbowSliderSpeedChange}/>
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
                  <Slider value={this.state.cycleSpeed} min={1} max={100} defaultValue={50} aria-label="Speed" size="small" valueLabelDisplay="auto" onChange={this.handleCycleSliderSpeedChange}/>
                </div>
              </TabPanel>
              <TabPanel value={this.state.value} index={4}>
              </TabPanel>
            </Card>
          </div>
          <div>
            <Card style={{margin:20}}>
              <Typography sx={{ fontSize: 22 }} color="text.secondary" gutterBottom>
                Alarm clock
              </Typography>
              <div style={{margin:20}}>
                {
                  this.state.alarms.map((alarm, alarm_nb) => {
                    console.log(alarm)
                    return <div style={{borderRadius:5, margin:10, paddingLeft:10, paddingRight:10, border: "1px solid #777777", flexDirection:'row', display:'flex', alignItems:'center'}}>
                      <Checkbox
                        checked={alarm.active}
                        onChange={(event)=>{
                          let a = this.state.alarms;
                          a[alarm_nb].active = event.target.checked;
                          this.setState({alarms:a});
                        }}
                        icon={<AlarmOffIcon />}
                        checkedIcon={<AlarmOnIcon />}
                      />
                      <div style={{display:'flex', marginLeft:20, alignItems:'center', justifyContent:'center'}}>
                        <BoltIcon color={this.state.alarms[alarm_nb].method=='ease'?"":"primary"}/>
                        <Switch
                          checked={this.state.alarms[alarm_nb].method=='ease'}
                          onChange={()=>{
                            let a = this.state.alarms
                            a[alarm_nb].method = (a[alarm_nb].method=='ease'?'flicker':'ease')
                            this.setState({alarms:a})
                          }}
                          color="default"/>
                        <MovingIcon color={this.state.alarms[alarm_nb].method=='ease'?"primary":""}/>
                      </div>
                      <Typography sx={{ fontSize: 22, marginTop:1, marginLeft:5 }} color="text.secondary" gutterBottom>
                        {(''+alarm.time.hour()).padStart(2, '0')}:{(''+alarm.time.minute()).padStart(2, '0')}
                      </Typography>
                      <div style={{flex:1}}/>
                      <IconButton onClick={()=>{
                          let a = this.state.alarms
                          a.splice(alarm_nb, 1)
                          this.setState({alarms:a})
                        }}>
                        <DeleteIcon />
                      </IconButton>
                    </div>
                  })
                }
              </div>
              <Button variant="outlined" startIcon={<AddAlarmIcon />} onClick={() => {this.setState({openingAlarmTimeSelector:true})}}>
                New Alarm
              </Button>
              <div style={{margin:20, display:this.state.openingAlarmTimeSelector?'flex':'none'}}>
                <LocalizationProvider dateAdapter={AdapterDayjs} color="secondary">
                  <StaticTimePicker
                    displayStaticWrapperAs="mobile"
                    value={this.state.alarmTime}
                    color="secondary"
                    disableOpenPicker
                    style={{backgroundColor:'red'}}
                    onChange={(newValue) => {
                      this.setState({alarmTime : newValue});
                    }}
                    onAccept={()=>{
                      let a = this.state.alarms
                      a.push({time:this.state.alarmTime, active:true, method:'ease'})
                      this.setState({alarms:a, openingAlarmTimeSelector:false})
                    }}
                    onCancel={()=>{
                      console.log('onClose')
                      this.setState({openingAlarmTimeSelector:false})
                    }}
                    renderInput={(params) => <TextField {...params} />}
                  />
                </LocalizationProvider>
              </div>
            </Card>
          </div>
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
