import { TrafficNetwork } from './types';

export function createSampleNetwork(): TrafficNetwork {
  return {
    segments: {
      // Times Square Area - High Traffic Intersections
      "times_square_42nd_7th": {
        id: "times_square_42nd_7th",
        name: "Times Square - 42nd St & 7th Ave",
        segment_type: "intersection",
        capacity: 2500.0,
        length: 60.0,
        coordinates: [[40.7589, -73.9851], [40.7590, -73.9850]],
        cycle_time: 180.0,
        green_time: 90.0,
        current_queue: 45.0,
        current_flow: 1850.0,
        police_control: true,
        police_reduction: 0.3,
        weather_factor: 1.0,
        green_time_adjustment: 0.0
      },
      "herald_square_34th_6th": {
        id: "herald_square_34th_6th",
        name: "Herald Square - 34th St & 6th Ave",
        segment_type: "intersection",
        capacity: 2200.0,
        length: 55.0,
        coordinates: [[40.7505, -73.9876], [40.7506, -73.9875]],
        cycle_time: 160.0,
        green_time: 75.0,
        current_queue: 38.0,
        current_flow: 1650.0,
        police_control: false,
        police_reduction: 0.5,
        weather_factor: 1.0,
        green_time_adjustment: 0.0
      },
      "union_square_14th_broadway": {
        id: "union_square_14th_broadway",
        name: "Union Square - 14th St & Broadway",
        segment_type: "intersection",
        capacity: 2000.0,
        length: 50.0,
        coordinates: [[40.7359, -73.9911], [40.7360, -73.9910]],
        cycle_time: 150.0,
        green_time: 70.0,
        current_queue: 32.0,
        current_flow: 1420.0,
        police_control: false,
        police_reduction: 0.5,
        weather_factor: 1.0,
        green_time_adjustment: 0.0
      },
      "columbus_circle_59th_broadway": {
        id: "columbus_circle_59th_broadway",
        name: "Columbus Circle - 59th St & Broadway",
        segment_type: "intersection",
        capacity: 2300.0,
        length: 65.0,
        coordinates: [[40.7681, -73.9819], [40.7682, -73.9818]],
        cycle_time: 170.0,
        green_time: 85.0,
        current_queue: 42.0,
        current_flow: 1750.0,
        police_control: false,
        police_reduction: 0.5,
        weather_factor: 1.0,
        green_time_adjustment: 0.0
      },
      "lincoln_tunnel_entrance": {
        id: "lincoln_tunnel_entrance",
        name: "Lincoln Tunnel Entrance - 40th St & 9th Ave",
        segment_type: "intersection",
        capacity: 2800.0,
        length: 70.0,
        coordinates: [[40.7564, -73.9925], [40.7565, -73.9924]],
        cycle_time: 200.0,
        green_time: 100.0,
        current_queue: 65.0,
        current_flow: 2100.0,
        police_control: true,
        police_reduction: 0.2,
        weather_factor: 1.0,
        green_time_adjustment: 0.0
      },
      
      // Major Roads and Avenues
      "broadway_42nd_to_34th": {
        id: "broadway_42nd_to_34th",
        name: "Broadway (42nd to 34th St)",
        segment_type: "road",
        capacity: 1800.0,
        length: 800.0,
        coordinates: [[40.7590, -73.9850], [40.7550, -73.9870], [40.7505, -73.9875]],
        current_queue: 55.0,
        current_flow: 1320.0,
        police_control: false,
        police_reduction: 0.5,
        weather_factor: 1.0,
        green_time_adjustment: 0.0
      },
      "broadway_34th_to_14th": {
        id: "broadway_34th_to_14th",
        name: "Broadway (34th to 14th St)",
        segment_type: "road",
        capacity: 1600.0,
        length: 2000.0,
        coordinates: [[40.7505, -73.9875], [40.7450, -73.9890], [40.7360, -73.9910]],
        current_queue: 48.0,
        current_flow: 1180.0,
        police_control: false,
        police_reduction: 0.5,
        weather_factor: 1.0,
        green_time_adjustment: 0.0
      },
      "seventh_avenue_59th_to_42nd": {
        id: "seventh_avenue_59th_to_42nd",
        name: "7th Avenue (59th to 42nd St)",
        segment_type: "road",
        capacity: 1700.0,
        length: 1700.0,
        coordinates: [[40.7682, -73.9818], [40.7640, -73.9835], [40.7590, -73.9850]],
        current_queue: 62.0,
        current_flow: 1450.0,
        police_control: false,
        police_reduction: 0.5,
        weather_factor: 1.0,
        green_time_adjustment: 0.0
      },
      "sixth_avenue_42nd_to_34th": {
        id: "sixth_avenue_42nd_to_34th",
        name: "6th Avenue (42nd to 34th St)",
        segment_type: "road",
        capacity: 1500.0,
        length: 800.0,
        coordinates: [[40.7540, -73.9857], [40.7520, -73.9865], [40.7505, -73.9875]],
        current_queue: 35.0,
        current_flow: 1150.0,
        police_control: false,
        police_reduction: 0.5,
        weather_factor: 1.0,
        green_time_adjustment: 0.0
      },
      "ninth_avenue_42nd_to_34th": {
        id: "ninth_avenue_42nd_to_34th",
        name: "9th Avenue (42nd to 34th St)",
        segment_type: "road",
        capacity: 1400.0,
        length: 800.0,
        coordinates: [[40.7565, -73.9924], [40.7540, -73.9930], [40.7515, -73.9935]],
        current_queue: 28.0,
        current_flow: 980.0,
        police_control: false,
        police_reduction: 0.5,
        weather_factor: 1.0,
        green_time_adjustment: 0.0
      },
      
      // Cross Streets
      "42nd_street_7th_to_9th": {
        id: "42nd_street_7th_to_9th",
        name: "42nd Street (7th to 9th Ave)",
        segment_type: "road",
        capacity: 1300.0,
        length: 600.0,
        coordinates: [[40.7590, -73.9850], [40.7575, -73.9890], [40.7565, -73.9924]],
        current_queue: 40.0,
        current_flow: 950.0,
        police_control: false,
        police_reduction: 0.5,
        weather_factor: 1.0,
        green_time_adjustment: 0.0
      },
      "34th_street_6th_to_9th": {
        id: "34th_street_6th_to_9th",
        name: "34th Street (6th to 9th Ave)",
        segment_type: "road",
        capacity: 1200.0,
        length: 900.0,
        coordinates: [[40.7505, -73.9875], [40.7510, -73.9900], [40.7515, -73.9935]],
        current_queue: 33.0,
        current_flow: 850.0,
        police_control: false,
        police_reduction: 0.5,
        weather_factor: 1.0,
        green_time_adjustment: 0.0
      },
      "14th_street_broadway_to_9th": {
        id: "14th_street_broadway_to_9th",
        name: "14th Street (Broadway to 9th Ave)",
        segment_type: "road",
        capacity: 1100.0,
        length: 1200.0,
        coordinates: [[40.7360, -73.9910], [40.7365, -73.9950], [40.7370, -73.9990]],
        current_queue: 25.0,
        current_flow: 720.0,
        police_control: false,
        police_reduction: 0.5,
        weather_factor: 1.0,
        green_time_adjustment: 0.0
      },
      
      // Highway Access
      "fdr_drive_access": {
        id: "fdr_drive_access",
        name: "FDR Drive Access - 23rd St",
        segment_type: "road",
        capacity: 2500.0,
        length: 1000.0,
        coordinates: [[40.7390, -73.9760], [40.7400, -73.9720], [40.7410, -73.9680]],
        current_queue: 75.0,
        current_flow: 1950.0,
        police_control: false,
        police_reduction: 0.5,
        weather_factor: 1.0,
        green_time_adjustment: 0.0
      },
      "west_side_highway_access": {
        id: "west_side_highway_access",
        name: "West Side Highway Access - 34th St",
        segment_type: "road",
        capacity: 2400.0,
        length: 800.0,
        coordinates: [[40.7515, -73.9935], [40.7520, -73.9970], [40.7525, -74.0005]],
        current_queue: 68.0,
        current_flow: 1820.0,
        police_control: false,
        police_reduction: 0.5,
        weather_factor: 1.0,
        green_time_adjustment: 0.0
      }
    },
    connections: {
      // Intersection connections
      "times_square_42nd_7th": ["broadway_42nd_to_34th", "seventh_avenue_59th_to_42nd", "42nd_street_7th_to_9th"],
      "herald_square_34th_6th": ["broadway_42nd_to_34th", "broadway_34th_to_14th", "sixth_avenue_42nd_to_34th", "34th_street_6th_to_9th"],
      "union_square_14th_broadway": ["broadway_34th_to_14th", "14th_street_broadway_to_9th"],
      "columbus_circle_59th_broadway": ["seventh_avenue_59th_to_42nd"],
      "lincoln_tunnel_entrance": ["ninth_avenue_42nd_to_34th", "42nd_street_7th_to_9th", "west_side_highway_access"],
      
      // Road segment connections
      "broadway_42nd_to_34th": ["times_square_42nd_7th", "herald_square_34th_6th"],
      "broadway_34th_to_14th": ["herald_square_34th_6th", "union_square_14th_broadway"],
      "seventh_avenue_59th_to_42nd": ["columbus_circle_59th_broadway", "times_square_42nd_7th"],
      "sixth_avenue_42nd_to_34th": ["herald_square_34th_6th"],
      "ninth_avenue_42nd_to_34th": ["lincoln_tunnel_entrance", "34th_street_6th_to_9th"],
      "42nd_street_7th_to_9th": ["times_square_42nd_7th", "lincoln_tunnel_entrance"],
      "34th_street_6th_to_9th": ["herald_square_34th_6th", "ninth_avenue_42nd_to_34th", "west_side_highway_access"],
      "14th_street_broadway_to_9th": ["union_square_14th_broadway"],
      "fdr_drive_access": [],
      "west_side_highway_access": ["lincoln_tunnel_entrance", "34th_street_6th_to_9th"]
    }
  };
}