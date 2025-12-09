from ..models.traffic import TrafficNetwork, TrafficSegment, SegmentType

def create_sample_network() -> TrafficNetwork:
    """
    Create a sample traffic network for demonstration purposes.
    This represents a simplified city intersection network.
    """
    
    segments = {}
    
    # Main Street intersections
    segments["intersection_main_1st"] = TrafficSegment(
        id="intersection_main_1st",
        name="Main St & 1st Ave",
        segment_type=SegmentType.INTERSECTION,
        capacity=1800.0,  # vehicles/hour
        length=50.0,  # meters
        coordinates=[(40.7589, -73.9851), (40.7590, -73.9850)],
        cycle_time=120.0,
        green_time=60.0,
        current_queue=5.0
    )
    
    segments["intersection_main_2nd"] = TrafficSegment(
        id="intersection_main_2nd",
        name="Main St & 2nd Ave",
        segment_type=SegmentType.INTERSECTION,
        capacity=1600.0,
        length=50.0,
        coordinates=[(40.7599, -73.9851), (40.7600, -73.9850)],
        cycle_time=120.0,
        green_time=55.0,
        current_queue=8.0
    )
    
    segments["intersection_main_3rd"] = TrafficSegment(
        id="intersection_main_3rd",
        name="Main St & 3rd Ave",
        segment_type=SegmentType.INTERSECTION,
        capacity=1700.0,
        length=50.0,
        coordinates=[(40.7609, -73.9851), (40.7610, -73.9850)],
        cycle_time=120.0,
        green_time=65.0,
        current_queue=3.0
    )
    
    # Broadway intersections
    segments["intersection_broadway_1st"] = TrafficSegment(
        id="intersection_broadway_1st",
        name="Broadway & 1st Ave",
        segment_type=SegmentType.INTERSECTION,
        capacity=2000.0,
        length=50.0,
        coordinates=[(40.7589, -73.9861), (40.7590, -73.9860)],
        cycle_time=140.0,
        green_time=70.0,
        current_queue=12.0
    )
    
    segments["intersection_broadway_2nd"] = TrafficSegment(
        id="intersection_broadway_2nd",
        name="Broadway & 2nd Ave",
        segment_type=SegmentType.INTERSECTION,
        capacity=1900.0,
        length=50.0,
        coordinates=[(40.7599, -73.9861), (40.7600, -73.9860)],
        cycle_time=140.0,
        green_time=65.0,
        current_queue=15.0
    )
    
    # Road segments connecting intersections
    segments["main_st_1st_to_2nd"] = TrafficSegment(
        id="main_st_1st_to_2nd",
        name="Main St (1st to 2nd Ave)",
        segment_type=SegmentType.ROAD,
        capacity=1400.0,
        length=300.0,
        coordinates=[(40.7590, -73.9850), (40.7595, -73.9850), (40.7599, -73.9850)],
        current_queue=20.0
    )
    
    segments["main_st_2nd_to_3rd"] = TrafficSegment(
        id="main_st_2nd_to_3rd",
        name="Main St (2nd to 3rd Ave)",
        segment_type=SegmentType.ROAD,
        capacity=1300.0,
        length=300.0,
        coordinates=[(40.7600, -73.9850), (40.7605, -73.9850), (40.7609, -73.9850)],
        current_queue=25.0
    )
    
    segments["broadway_1st_to_2nd"] = TrafficSegment(
        id="broadway_1st_to_2nd",
        name="Broadway (1st to 2nd Ave)",
        segment_type=SegmentType.ROAD,
        capacity=1600.0,
        length=350.0,
        coordinates=[(40.7590, -73.9860), (40.7595, -73.9860), (40.7599, -73.9860)],
        current_queue=30.0
    )
    
    segments["1st_ave_main_to_broadway"] = TrafficSegment(
        id="1st_ave_main_to_broadway",
        name="1st Ave (Main to Broadway)",
        segment_type=SegmentType.ROAD,
        capacity=1200.0,
        length=250.0,
        coordinates=[(40.7589, -73.9850), (40.7589, -73.9855), (40.7589, -73.9860)],
        current_queue=10.0
    )
    
    segments["2nd_ave_main_to_broadway"] = TrafficSegment(
        id="2nd_ave_main_to_broadway",
        name="2nd Ave (Main to Broadway)",
        segment_type=SegmentType.ROAD,
        capacity=1100.0,
        length=250.0,
        coordinates=[(40.7599, -73.9850), (40.7599, -73.9855), (40.7599, -73.9860)],
        current_queue=18.0
    )
    
    # Highway access road (high capacity, potential bottleneck)
    segments["highway_access"] = TrafficSegment(
        id="highway_access",
        name="Highway Access Road",
        segment_type=SegmentType.ROAD,
        capacity=2200.0,
        length=500.0,
        coordinates=[(40.7609, -73.9850), (40.7615, -73.9845), (40.7620, -73.9840)],
        current_queue=45.0
    )
    
    # Define network connections (simplified)
    connections = {
        "intersection_main_1st": ["main_st_1st_to_2nd", "1st_ave_main_to_broadway"],
        "intersection_main_2nd": ["main_st_1st_to_2nd", "main_st_2nd_to_3rd", "2nd_ave_main_to_broadway"],
        "intersection_main_3rd": ["main_st_2nd_to_3rd", "highway_access"],
        "intersection_broadway_1st": ["broadway_1st_to_2nd", "1st_ave_main_to_broadway"],
        "intersection_broadway_2nd": ["broadway_1st_to_2nd", "2nd_ave_main_to_broadway"],
        "main_st_1st_to_2nd": ["intersection_main_1st", "intersection_main_2nd"],
        "main_st_2nd_to_3rd": ["intersection_main_2nd", "intersection_main_3rd"],
        "broadway_1st_to_2nd": ["intersection_broadway_1st", "intersection_broadway_2nd"],
        "1st_ave_main_to_broadway": ["intersection_main_1st", "intersection_broadway_1st"],
        "2nd_ave_main_to_broadway": ["intersection_main_2nd", "intersection_broadway_2nd"],
        "highway_access": ["intersection_main_3rd"]
    }
    
    return TrafficNetwork(
        segments=segments,
        connections=connections
    )