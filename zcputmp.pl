#!/usr/bin/perl -w
#
#fitletCPUtemp.pl

# Darryl Hassell 8/4/2018

use Tk;
use List::MoreUtils qw(first_index);
use Device::SerialPort;
use Time::HiRes ('sleep');

# Define & Initialize Variables

my $CPU_Temp = 0.0;
my $CPU_Temp_Color = '#FFFFFF';
my $Element = 0;

# Configure Serial Port
my $port = Device::SerialPort -> new("/dev/ttyACM0");
$port -> baudrate(115200);
$port -> databits(8);
$port -> parity("none");
$port -> stopbits(1);
$port -> write_settings;

# Set Sleep Delay After Writes in Seconds
our $delay = 0.1;

# Initialize fit-statUSB to Red - Green - Blue - White
$port -> write("#FF0000\n");
$port -> purge_rx;
sleep(2);

$port -> write("#00FF00\n");
$port -> purge_rx;
sleep(2);

$port -> write("#0000FF\n");
$port -> purge_rx;
sleep(2);

$port -> write("#FFFFFF\n");
$port -> purge_rx;
sleep(2);


# Create Main Window
$WinMain = MainWindow->new;
$WinMain -> resizable (0,0);

# Label Main Window
$myframe = $WinMain -> Frame ->pack();
$CPU_Temp_Label = $myframe -> Label (-text => 'fitlet CPU Temp Monitor'."\n"."$CPU_Temp".' Deg. C.', -background => "$CPU_Temp_Color", -font => "helvetica 9 bold")->pack(-ipadx => 20,-ipady => 20);

# Exit Program Button
$stopbutton = $myframe -> Button (-text => 'Exit', -command => \&Exit, -foreground => 'black', -background => 'lightblue');
$stopbutton -> pack (-side => 'bottom');

$WinMain -> repeat(2000, \&GetCPUTemp);

MainLoop();

################################ Exit Program ################################

sub Exit {

$port -> write("#000000\n");
$port -> purge_rx;
sleep($delay);
exit;
}

################################ CPU Temperature Data ################################

sub GetCPUTemp {

$CPU_Temp_Unfiltered1 = `sensors`;

# Read Unfiltered CPU Temperature Data Into Array
@CPU_Temp_Array1 = split ' ', $CPU_Temp_Unfiltered1;

# Determine Array Index of CPU Indicator k10temp-pci-00c3
my $ArrayIndex1 = first_index { $_ eq 'k10temp-pci-00c3' } @CPU_Temp_Array1;

# Determine Array Index of CPU Temperature
my $ArrayIndex2 = $ArrayIndex1 + 5;

# Read CPU Temp Out Of Array
$CPU_Temp_Unfiltered2 = $CPU_Temp_Array1[$ArrayIndex2];

# Capture Only Numbers From String
@CPU_Temp_Array2 = split '°', $CPU_Temp_Unfiltered2;

$CPU_Temp = $CPU_Temp_Array2[0];

if ($CPU_Temp <= 30){
$CPU_Temp_Color = '#0000FF';
$port -> write("#0000FF\n");
$port -> purge_rx;
sleep($delay);
}

elsif ($CPU_Temp > 30 && $CPU_Temp <= 32){
$CPU_Temp_Color = '#0079FF';
$port -> write("#0079FF\n");
$port -> purge_rx;
sleep($delay);
}

elsif ($CPU_Temp > 32 && $CPU_Temp <= 34){
$CPU_Temp_Color = '#00FFFA';
$port -> write("#00FFFA\n");
$port -> purge_rx;
sleep($delay);
}

elsif ($CPU_Temp > 34 && $CPU_Temp <= 36){
$CPU_Temp_Color = '#00FF67';
$port -> write("#00FF67\n");
$port -> purge_rx;
sleep($delay);
}

elsif ($CPU_Temp > 36 && $CPU_Temp <= 38){
$CPU_Temp_Color = '#00FF00';
$port -> write("#00FF00\n");
$port -> purge_rx;
sleep($delay);
}

elsif ($CPU_Temp > 38 && $CPU_Temp <= 40){
$CPU_Temp_Color = '#37FF00';
$port -> write("#37FF00\n");
$port -> purge_rx;
sleep($delay);
}

elsif ($CPU_Temp > 40 && $CPU_Temp <= 42){
$CPU_Temp_Color = '#85FF00';
$port -> write("#85FF00\n");
$port -> purge_rx;
sleep($delay);
}

elsif ($CPU_Temp > 42 && $CPU_Temp <= 44){
$CPU_Temp_Color = '#BEFF00';
$port -> write("#BEFF00\n");
$port -> purge_rx;
sleep($delay);
}

elsif ($CPU_Temp > 44 && $CPU_Temp <= 46){
$CPU_Temp_Color = '#FFFF00';
$port -> write("#FFFF00\n");
$port -> purge_rx;
sleep($delay);
}

elsif ($CPU_Temp > 46 && $CPU_Temp <= 48){
$CPU_Temp_Color = '#FFEB00';
$port -> write("#FFEB00\n");
$port -> purge_rx;
sleep($delay);
}

elsif ($CPU_Temp > 48 && $CPU_Temp <= 50){
$CPU_Temp_Color = '#FFDA00';
$port -> write("#FFDA00\n");
$port -> purge_rx;
sleep($delay);
}

elsif ($CPU_Temp > 50 && $CPU_Temp <= 52){
$CPU_Temp_Color = '#FFCC00';
$port -> write("#FFCC00\n");
$port -> purge_rx;
sleep($delay);
}

elsif ($CPU_Temp > 52 && $CPU_Temp <= 54){
$CPU_Temp_Color = '#FFA500';
$port -> write("#FFA500\n");
$port -> purge_rx;
sleep($delay);
}

elsif ($CPU_Temp > 54 && $CPU_Temp <= 56){
$CPU_Temp_Color = '#FF8800';
$port -> write("#FF8800\n");
$port -> purge_rx;
sleep($delay);
}

elsif ($CPU_Temp > 56 && $CPU_Temp <= 58){
$CPU_Temp_Color = '#FF6500';
$port -> write("#FF6500\n");
$port -> purge_rx;
sleep($delay);
}

elsif ($CPU_Temp > 58 && $CPU_Temp <= 60){
$CPU_Temp_Color = '#FF3700';
$port -> write("#FF3700\n");
$port -> purge_rx;
sleep($delay);
}

elsif ($CPU_Temp > 60 && $CPU_Temp <= 62){
$CPU_Temp_Color = '#FF0000';
$port -> write("#FF0000\n");
$port -> purge_rx;
sleep($delay);
}

elsif ($CPU_Temp > 62 && $CPU_Temp <= 64){
$CPU_Temp_Color = '#FF003E';
$port -> write("#FF003E\n");
$port -> purge_rx;
sleep($delay);
}

elsif ($CPU_Temp > 64 && $CPU_Temp <= 66){
$CPU_Temp_Color = '#FF0097';
$port -> write("#FF0097\n");
$port -> purge_rx;
sleep($delay);
}

elsif ($CPU_Temp > 66 && $CPU_Temp <= 68){
$CPU_Temp_Color = '#FF00BD';
$port -> write("#FF00BD\n");
$port -> purge_rx;
sleep($delay);
}

elsif ($CPU_Temp > 68 && $CPU_Temp <= 70){
$CPU_Temp_Color = '#FF00CA';
$port -> write("#FF00CA\n");
$port -> purge_rx;
sleep($delay);
}

else {
$CPU_Temp_Color = '#FFB6F5';
$port -> write("#FFB6F5\n");
$port -> purge_rx;
sleep($delay);
}

$CPU_Temp_Label -> configure (-text => 'fitlet CPU Temp Monitor'."\n"."$CPU_Temp".' Deg. C.', -background => "$CPU_Temp_Color");

}