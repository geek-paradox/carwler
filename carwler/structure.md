- db
  - tables
    - brand
      - id
      - name
      - url
    - model
      - id
      - brand_id
      - name
      - url
      - body_type
    - variant
      - id
      - model_id
      - name
      - url
      - fuel_type
      - transmission_type
      - price
      - specs_short_description
    - spec_category
      - id
      - name
        * Engine & Transmission
        * Dimensions & Weight
        * Capacity
        * Suspensions, Brakes & Steering
    - feature_category
      - id
      - name
        * Safety
        * Braking & Traction
        * Locks & Security
        * Comfort & Convenience
        * Seats & Upholstery
        * Storage
        * Doors, Windows, Mirrors & Wipers
        * Exterior
        * Lighting
        * Instrumentation
        * Manufacturer Warranty
    - specification
      - id
      - spec_category_id
      - name
    - variant_specs
      - variant_id
      - engine
      - engine_type
      - max_power
      - max_torque
      - mileage
      - transmission
      - length
      - width
      - height
      - wheelbase
      - ground_clearance
      - kerb_weight
      - doors
      - seating_capacity
      - seating_rows
      - bootspace
      - fuel_tank_capacity
      - suspension_front
      - suspension_rear
      - front_break_type
      - rear_brake_type
      - minimum_turning_radius
      - steering_type
      - wheels
      - spare_wheel
      - front_tyres
      - rear_tyres
    - variant_features
      - variant_id
      - feature_type_id
    - default_units
      - specification_id
      - unit